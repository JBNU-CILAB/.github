#!/usr/bin/env python3
"""JBNU-CILAB 조직 프로필 README를 생성한다.

연구실 콘텐츠의 단일 진실 공급원은 JBNU-CILAB.github.io/_data/*.yml 이다.
이 스크립트는 해당 데이터를 읽어 profile/README.template.md 의 AUTO:* 마커
구간에 렌더링한 뒤 profile/README.md 로 저장하기만 한다.

두 개의 독립된 트랙으로 동작한다.

  static   YAML -> 헤더 / 연구 분야 / 프로젝트 / 소식 / 논문.
           YAML 조회 외에 API 호출이 없으므로 항상 성공해야 한다.

  activity members.yml 의 github_activity: true -> GitHub GraphQL.
           실패가 허용된다. 오류가 나면 data/activity-cache.json 의 직전
           결과를 재사용하므로 섹션이 빈 채로 덮어써지지 않는다.

공개 저장소에 대한 공개 기여만 집계하며, 멤버 이메일은 절대 출력하지 않는다.
자세한 설계 배경은 ../README.md 참고.
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import yaml

# ── 설정 ───────────────────────────────────────────────────────────────────
SOURCE_REPO = "JBNU-CILAB/JBNU-CILAB.github.io"
FALLBACK_SITE_URL = "https://cilab.jbnu.ac.kr"

MAX_NEWS = 5
MAX_PUBLICATIONS = 5
MAX_ACTIVE_REPOS = 5

# 멤버별 커밋/PR 수는 의도적으로 감춘다. 조직 첫 화면에 공개 리더보드를 두면
# 멤버 사이에 비교 압박이 생긴다. True 로 바꾸면 수치가 표에 함께 표시된다.
SHOW_MEMBER_COUNTS = False

# 멤버들은 수업 과제나 개인 프로젝트 저장소에도 활발히 커밋한다. 조직 소유
# 저장소와 projects.yml 에 등록된 저장소만 집계해, 관련성 판단 기준도 같은
# 단일 진실 공급원에서 나오도록 한다.
LAB_ORG = "JBNU-CILAB"
RESTRICT_TO_LAB_REPOS = True

KST = timezone(timedelta(hours=9))
ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "profile" / "README.template.md"
OUTPUT = ROOT / "profile" / "README.md"
CACHE = ROOT / "data" / "activity-cache.json"

API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
SESSION = requests.Session()
SESSION.headers.update({
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "jbnu-cilab-profile-builder",
})
if TOKEN:
    SESSION.headers["Authorization"] = f"Bearer {TOKEN}"


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def field(item: dict, key: str, default: str = "") -> str:
    return str(item.get(key) or default).strip()


# ── 원본 데이터 ────────────────────────────────────────────────────────────
def fetch_yaml(path: str):
    """사이트 저장소의 기본 브랜치에서 YAML 파일을 읽는다."""
    resp = SESSION.get(f"{API}/repos/{SOURCE_REPO}/contents/{path}", timeout=30)
    resp.raise_for_status()
    text = base64.b64decode(resp.json()["content"]).decode("utf-8")
    return yaml.safe_load(text) or {}


# ── 멤버 활동 ──────────────────────────────────────────────────────────────
ACTIVITY_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login
    name
    url
    contributionsCollection(from: $from, to: $to) {
      commitContributionsByRepository(maxRepositories: 100) {
        repository { nameWithOwner url isPrivate }
        contributions { totalCount }
      }
      pullRequestContributionsByRepository(maxRepositories: 100) {
        repository { nameWithOwner url isPrivate }
        contributions { totalCount }
      }
    }
  }
}
"""


def graphql(query: str, variables: dict) -> dict:
    resp = SESSION.post(
        f"{API}/graphql",
        json={"query": query, "variables": variables},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"][0].get("message", "GraphQL error"))
    return payload["data"]


def lab_repositories(projects: list) -> set:
    """projects.yml 에 등록된 저장소 슬러그 집합."""
    prefix = "https://github.com/"
    slugs = set()
    for project in projects:
        url = field(project, "github")
        if url.startswith(prefix):
            slugs.add(url[len(prefix):].strip("/").lower())
    return slugs


def is_lab_repository(name_with_owner: str, lab_repos: set) -> bool:
    if not RESTRICT_TO_LAB_REPOS:
        return True
    slug = name_with_owner.lower()
    return slug in lab_repos or slug.startswith(f"{LAB_ORG.lower()}/")


def opted_in_members(members: list) -> list:
    return [
        m for m in members
        if isinstance(m, dict) and m.get("github_activity") and field(m, "github")
    ]


def fetch_activity(members: list, lab_repos: set) -> dict:
    """올해 누적된 멤버별 공개 기여를 수집한다.

    비공개 기여는 두 겹으로 차단된다. 토큰이 멤버 본인의 것이 아니므로 GraphQL
    이 애초에 공개 활동만 반환하고, 비공개 저장소는 아래에서 한 번 더 걸러진다.
    연구실과 무관한 저장소도 함께 제외한다.
    """
    now = datetime.now(KST)
    since = datetime(now.year, 1, 1, tzinfo=KST)
    window = {
        "from": since.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "to": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    rows = []
    for member in opted_in_members(members):
        login = field(member, "github")
        user = graphql(ACTIVITY_QUERY, {"login": login, **window}).get("user")
        if not user:
            log(f"  ! 존재하지 않는 GitHub 계정, 건너뜀: {login}")
            continue

        repos: dict[str, dict] = {}
        collection = user["contributionsCollection"]
        for api_field, counter in (
            ("commitContributionsByRepository", "commits"),
            ("pullRequestContributionsByRepository", "pull_requests"),
        ):
            for entry in collection[api_field]:
                repo = entry["repository"]
                if repo["isPrivate"]:
                    continue
                if not is_lab_repository(repo["nameWithOwner"], lab_repos):
                    continue
                slot = repos.setdefault(repo["nameWithOwner"], {
                    "name_with_owner": repo["nameWithOwner"],
                    "url": repo["url"],
                    "commits": 0,
                    "pull_requests": 0,
                })
                slot[counter] += entry["contributions"]["totalCount"]

        ranked = sorted(
            repos.values(),
            key=lambda r: r["commits"] + r["pull_requests"],
            reverse=True,
        )
        rows.append({
            "login": user["login"],
            "display_name": field(member, "name_ko") or user.get("name") or user["login"],
            "group": field(member, "group"),
            "url": user["url"],
            "commits": sum(r["commits"] for r in ranked),
            "pull_requests": sum(r["pull_requests"] for r in ranked),
            "repos": ranked,
        })
        log(f"  · {login}: 연구실 저장소 {len(ranked)}곳")

    return {
        "year": now.year,
        # 데이터가 마지막으로 "바뀐" 날짜. 마지막으로 조회한 날짜가 아니다.
        # 아래 main() 에서 내용이 동일하면 캐시를 다시 쓰지 않기 때문이다.
        "as_of": now.strftime("%Y-%m-%d"),
        "members": rows,
    }


def load_cache() -> dict | None:
    if not CACHE.exists():
        return None
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        log(f"  ! 활동 캐시를 읽을 수 없음: {exc}")
        return None


# ── 섹션 렌더링 ────────────────────────────────────────────────────────────
def render_header(config: dict, professor: dict) -> str:
    lab = config.get("lab", {}) or {}
    pi = config.get("pi", {}) or {}

    name_ko = field(lab, "name_ko", field(config, "title"))
    name_en = field(lab, "name_en", field(config, "subtitle"))
    affiliation = " ".join(
        part for part in (field(lab, "university"), field(lab, "department")) if part
    )

    pi_link = ""
    for entry in professor.get("links", []) or []:
        if field(entry, "name").lower() == "github":
            pi_link = field(entry, "url")
            break
    pi_name = field(pi, "name_ko")
    pi_title = field(pi, "title").split("(")[0].strip()
    pi_text = f"[{pi_name}]({pi_link})" if pi_link else pi_name

    lines = [f"# {name_ko}"]
    if name_en:
        lines += ["", f"**{name_en}**"]
    if affiliation:
        lines += ["", affiliation]
    if pi_name:
        lines += ["", f"지도교수 · {pi_text} {pi_title}".rstrip()]
    return "\n".join(lines)


def render_research(research: list, site: str) -> str:
    lines = []
    for area in research:
        icon = field(area, "icon")
        title = field(area, "title")
        anchor = field(area, "id")
        link = f"{site}/research/#{anchor}" if anchor else f"{site}/research/"
        heading = f"{icon} {title}".strip()
        lines.append(f"### [{heading}]({link})")
        desc = field(area, "desc")
        if desc:
            lines += ["", desc]
        keywords = area.get("keywords") or []
        if keywords:
            lines += ["", " ".join(f"`{kw}`" for kw in keywords)]
        lines.append("")
    return "\n".join(lines).strip()


def render_projects(projects: list) -> str:
    def table(rows: list) -> list:
        out = ["| 프로젝트 | 설명 | 저장소 |", "| --- | --- | --- |"]
        for project in rows:
            url = field(project, "github")
            slug = url.replace("https://github.com/", "") if url else ""
            repo = f"[`{slug}`]({url})" if url else "—"
            out.append(
                f"| **{field(project, 'name')}** | {field(project, 'subtitle')} | {repo} |"
            )
        return out

    lines = []
    for label, group in (("참여 오픈소스 프로젝트", "opensource"),
                         ("자체 개발 프로젝트", "cilab")):
        rows = [p for p in projects if p.get("group") == group]
        if not rows:
            continue
        if lines:
            lines.append("")
        lines += [f"**{label}**", ""] + table(rows)
    return "\n".join(lines).strip()


def render_news(news: list, site: str) -> str:
    lines = []
    for item in news[:MAX_NEWS]:
        lines.append(f"- **{field(item, 'date')}** {field(item, 'badge')} — {field(item, 'text')}")
        note = field(item, "note")
        if note:
            lines.append(f"  <br>{note}")
    lines += ["", f"[전체 소식 보기 →]({site}/news/)"]
    return "\n".join(lines).strip()


def render_publications(publications: list, site: str) -> str:
    lines = []
    for paper in publications[:MAX_PUBLICATIONS]:
        title = field(paper, "title")
        link = field(paper, "link")
        headline = f"[{title}]({link})" if link else title
        award = field(paper, "award")
        lines.append(f"- **{headline}**" + (f" 🏆 {award}" if award else ""))
        detail = " — ".join(
            part for part in (field(paper, "authors"), field(paper, "venue")) if part
        )
        if detail:
            lines.append(f"  <br>{detail}")
    lines += ["", f"[전체 논문 목록 →]({site}/publication/)"]
    return "\n".join(lines).strip()


def render_activity(activity: dict) -> str:
    year = activity.get("year", "")
    active = [m for m in activity.get("members", []) if m["repos"]]

    lines = [
        f"> {year}년 1월 1일부터 집계한 연구실·오픈소스 프로젝트 저장소 공개 기여"
        " 내역입니다. 사이트 저장소의 `members.yml` 에서 `github_activity` 를"
        " 활성화한 멤버만 표시되며, 비공개 저장소와 비공개 기여는 집계에서"
        " 제외됩니다.",
        "",
    ]

    if not active:
        lines.append("_올해 집계된 공개 기여가 아직 없습니다._")
        return "\n".join(lines)

    if SHOW_MEMBER_COUNTS:
        lines += ["| 멤버 | 커밋 | PR | 활동 저장소 |", "| --- | ---: | ---: | --- |"]
    else:
        lines += ["| 멤버 | 활동 저장소 |", "| --- | --- |"]

    for member in active:
        who = f"[{member['display_name']}]({member['url']})"
        shown = member["repos"][:MAX_ACTIVE_REPOS]
        listed = ", ".join(f"[`{r['name_with_owner']}`]({r['url']})" for r in shown)
        hidden = len(member["repos"]) - len(shown)
        if hidden > 0:
            listed += f" 외 {hidden}곳"
        if SHOW_MEMBER_COUNTS:
            lines.append(
                f"| {who} | {member['commits']} | {member['pull_requests']} | {listed} |"
            )
        else:
            lines.append(f"| {who} | {listed} |")

    total_commits = sum(m["commits"] for m in active)
    total_prs = sum(m["pull_requests"] for m in active)
    repo_count = len({r["name_with_owner"] for m in active for r in m["repos"]})
    lines += [
        "",
        f"{year}년 연구실 전체 — 공개 저장소 **{repo_count}**곳에 커밋 "
        f"**{total_commits}**건, Pull Request **{total_prs}**건.",
    ]
    return "\n".join(lines)


# ── 템플릿 조립 ────────────────────────────────────────────────────────────
MARKER_RE = re.compile(
    r"<!-- AUTO:(?P<name>[A-Z_]+):START -->.*?<!-- AUTO:(?P=name):END -->",
    re.DOTALL,
)


def fill_markers(template: str, sections: dict) -> str:
    seen = set()

    def replace(match: re.Match) -> str:
        name = match.group("name")
        seen.add(name)
        if name not in sections:
            raise SystemExit(f"템플릿에 AUTO:{name} 마커가 있으나 렌더러가 없습니다")
        return f"<!-- AUTO:{name}:START -->\n{sections[name].strip()}\n<!-- AUTO:{name}:END -->"

    result = MARKER_RE.sub(replace, template)
    unused = sorted(set(sections) - seen)
    if unused:
        raise SystemExit(f"템플릿에 대응 마커가 없는 섹션: {unused}")
    return result


def main() -> int:
    refresh_activity = os.environ.get("REFRESH_ACTIVITY", "true").lower() == "true"

    log(f"{SOURCE_REPO} 에서 원본 데이터를 읽는 중")
    config = fetch_yaml("_config.yml")
    professor = fetch_yaml("_data/professor.yml")
    research = fetch_yaml("_data/research.yml")
    projects = fetch_yaml("_data/projects.yml")
    news = fetch_yaml("_data/news.yml")
    publications = fetch_yaml("_data/publications.yml")
    members = fetch_yaml("_data/members.yml")
    site = field(config, "url", FALLBACK_SITE_URL).rstrip("/")

    cached = load_cache()
    empty = {"year": datetime.now(KST).year, "as_of": "", "members": []}
    if refresh_activity:
        log(f"멤버 활동 수집 중 (연동 동의 {len(opted_in_members(members))}명)")
        try:
            activity = fetch_activity(members, lab_repositories(projects))
            if cached and cached.get("members") == activity["members"] \
                    and cached.get("year") == activity["year"]:
                log("  · 활동 내역에 변화가 없어 캐시를 유지합니다")
                activity = cached
            else:
                CACHE.parent.mkdir(parents=True, exist_ok=True)
                CACHE.write_text(
                    json.dumps(activity, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
        except Exception as exc:  # 네트워크 / rate limit / 스키마 변경
            log(f"  ! 활동 갱신 실패: {exc}")
            if cached is None:
                log("  ! 폴백할 캐시가 없어 빈 섹션으로 렌더링합니다")
                activity = empty
            else:
                log(f"  · {cached.get('as_of')} 캐시를 재사용합니다")
                activity = cached
    elif cached is None:
        log("활동 갱신을 건너뛰었으나 캐시가 없어 빈 섹션으로 렌더링합니다")
        activity = empty
    else:
        log(f"활동 갱신 생략 — {cached.get('as_of')} 캐시 재사용")
        activity = cached

    sections = {
        "HEADER": render_header(config, professor),
        "RESEARCH": render_research(research, site),
        "PROJECTS": render_projects(projects),
        "NEWS": render_news(news, site),
        "PUBLICATIONS": render_publications(publications, site),
        "ACTIVITY": render_activity(activity),
    }

    rendered = fill_markers(TEMPLATE.read_text(encoding="utf-8"), sections)
    if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered:
        log("profile/README.md 는 이미 최신 상태입니다")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    log("profile/README.md 를 갱신했습니다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
