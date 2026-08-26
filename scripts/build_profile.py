#!/usr/bin/env python3
"""JBNU-CILAB 조직 프로필 README 의 멤버 활동 섹션을 생성한다.

페이지의 대부분은 profile/README.template.md 에서 수기로 관리한다. 이 스크립트가
채우는 것은 AUTO:ACTIVITY 마커 구간 하나뿐이며, 그러기 위해 홈페이지 저장소에서
두 파일만 읽는다.

  _data/members.yml   활동 연동에 동의한 멤버의 GitHub 계정
  _data/projects.yml  연구실 저장소 판별에 쓰는 프로젝트 목록

활동 수집은 실패가 허용된다. 오류가 나면 data/activity-cache.json 의 직전 결과를
재사용하므로 섹션이 빈 채로 덮어써지지 않는다. 공개 저장소에 대한 공개 기여만
집계하며, 멤버 이메일과 실명은 출력하지 않는다.
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


def fetch_yaml(path: str):
    """홈페이지 저장소의 기본 브랜치에서 YAML 파일을 읽는다."""
    resp = SESSION.get(f"{API}/repos/{SOURCE_REPO}/contents/{path}", timeout=30)
    resp.raise_for_status()
    text = base64.b64decode(resp.json()["content"]).decode("utf-8")
    return yaml.safe_load(text) or []


# ── 멤버 활동 ──────────────────────────────────────────────────────────────
ACTIVITY_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login
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

    집계 연도는 실행 시점을 기준으로 자동으로 넘어간다.

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


def render_activity(activity: dict) -> str:
    year = activity.get("year", "")
    active = [m for m in activity.get("members", []) if m["repos"]]

    lines = [
        f"> Public contributions to lab and upstream project repositories since"
        f" January 1, {year}. Private repositories and private contributions are"
        " excluded.",
        "",
    ]

    if not active:
        lines.append("_No public contributions recorded yet this year._")
        return "\n".join(lines)

    if SHOW_MEMBER_COUNTS:
        lines += ["| Member | Commits | PRs | Active in |", "| --- | ---: | ---: | --- |"]
    else:
        lines += ["| Member | Active in |", "| --- | --- |"]

    for member in active:
        who = f"[@{member['login']}]({member['url']})"
        shown = member["repos"][:MAX_ACTIVE_REPOS]
        listed = ", ".join(f"[`{r['name_with_owner']}`]({r['url']})" for r in shown)
        hidden = len(member["repos"]) - len(shown)
        if hidden > 0:
            listed += f" +{hidden} more"
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
        f"In {year} the lab made **{total_commits}** commits and **{total_prs}** "
        f"pull requests across **{repo_count}** public repositories.",
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

    cached = load_cache()
    current_year = datetime.now(KST).year
    empty = {"year": current_year, "as_of": "", "members": []}

    # 집계 연도는 실행 시점 기준으로 자동으로 넘어간다. 다만 push 로 트리거된
    # 실행은 활동을 갱신하지 않으므로, 해가 바뀐 직후에는 지난해 집계가 그대로
    # 남을 수 있다. 캐시 연도가 올해와 다르면 트리거와 무관하게 갱신한다.
    if not refresh_activity and cached and cached.get("year") != current_year:
        log(f"캐시가 {cached.get('year')}년 집계라 {current_year}년으로 강제 갱신합니다")
        refresh_activity = True

    if refresh_activity:
        try:
            # 홈페이지 저장소는 활동 집계에만 필요하다. 갱신하지 않는 실행에서는
            # 아예 읽지 않으므로, 불필요한 호출도 실패 지점도 생기지 않는다.
            log(f"{SOURCE_REPO} 에서 멤버·프로젝트 목록을 읽는 중")
            members = fetch_yaml("_data/members.yml")
            projects = fetch_yaml("_data/projects.yml")
            log(f"멤버 활동 수집 중 (연동 동의 {len(opted_in_members(members))}명)")
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

    rendered = fill_markers(
        TEMPLATE.read_text(encoding="utf-8"),
        {"ACTIVITY": render_activity(activity)},
    )
    if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") == rendered:
        log("profile/README.md 는 이미 최신 상태입니다")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    log("profile/README.md 를 갱신했습니다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
