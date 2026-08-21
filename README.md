# JBNU-CILAB/.github

<https://github.com/JBNU-CILAB> 조직 첫 화면에 표시되는 프로필 페이지를 자동으로
생성하는 저장소입니다.

연구실 콘텐츠의 단일 진실 공급원은 홈페이지 저장소인
[JBNU-CILAB.github.io][site] 입니다. 이 저장소는 연구실 데이터를 직접 보관하지
않고, 홈페이지 저장소의 데이터를 읽어 `profile/README.md` 를 주기적으로 생성하는
역할만 합니다.

[site]: https://github.com/JBNU-CILAB/JBNU-CILAB.github.io

## 구성

| 경로 | 역할 |
| --- | --- |
| `profile/README.template.md` | 직접 편집하는 원본. 소개 문구와 `AUTO:*` 마커. |
| `profile/README.md` | **생성물.** 직접 편집하지 마세요, 덮어써집니다. |
| `scripts/build_profile.py` | 렌더러. |
| `data/activity-cache.json` | **생성물.** 마지막 멤버 활동 데이터 (폴백용). |
| `.github/workflows/update-profile.yml` | 스케줄러. |

## 동작 방식

홈페이지 저장소는 데이터가 바뀌어도 이 저장소에 알려줄 수 없습니다. 그래서 두
개의 cron 과 수동 트리거로 동작합니다.

- **매일 06:00 KST** — `_data/*.yml` 을 읽어 다시 렌더링합니다. GraphQL 호출 없음.
- **매주 월요일 06:30 KST** — 위와 동일 + 멤버 활동 갱신.
- **`workflow_dispatch`** — 수동 실행. 기본값으로 활동까지 갱신합니다.

활동 갱신을 매일이 아니라 매주 돌리는 데에는 이유가 있습니다. 기여 수치는 멤버가
커밋하는 것만으로 저절로 변하기 때문에, 매일 갱신하면 편집상 의미가 없는 봇 커밋이
매일 쌓입니다.

두 트랙은 서로 독립적입니다. 헤더 / 연구 분야 / 프로젝트 / 소식 / 논문은 YAML 만
읽으면 되므로 항상 렌더링됩니다. 멤버 활동은 GitHub API 에 의존하며 실패가
허용됩니다. 오류가 나면 `data/activity-cache.json` 의 직전 결과를 다시 읽어오므로
섹션이 조용히 비워지는 일은 없습니다.

렌더링 결과가 실제로 달라진 경우에만 커밋합니다.

## 무엇을 공개하고, 무엇을 공개하지 않는가

멤버 활동 연동은 옵트인입니다. `_data/members.yml` 항목에 `github` 계정과
`github_activity: true` 가 **모두** 있는 멤버만 표시됩니다.

옵트인 위에 다음 제한을 추가로 둡니다.

- **비공개 기여는 제외됩니다.** 워크플로는 저장소 범위의 `GITHUB_TOKEN` 으로
  인증하며 이는 멤버 본인의 토큰이 아니므로, GraphQL 이 애초에 공개 활동만
  반환합니다. 그 위에 비공개 저장소를 코드에서 한 번 더 걸러냅니다.
- **연구실과 무관한 저장소는 제외됩니다.** 조직 소유 저장소와
  `_data/projects.yml` 에 등록된 저장소만 집계하므로, 수업 과제나 개인
  프로젝트가 연구실 첫 화면에 올라오지 않습니다. `RESTRICT_TO_LAB_REPOS` 참고.
- **멤버별 커밋 수는 표시하지 않습니다.** 조직 첫 화면에 공개 리더보드를 두면
  멤버가 순위로 비교됩니다. 각자 활동한 저장소 목록과 연구실 전체 합계만
  보여줍니다. 바꾸려면 `SHOW_MEMBER_COUNTS` 를 `True` 로 두세요.
- **이메일은 절대 출력하지 않습니다.** `members.yml` 에 이메일이 들어 있지만,
  조직 프로필은 크롤러가 수집해 가는 공개 페이지입니다.

## 내용 수정하기

홈페이지 저장소의 [`_data/`][data] 아래 해당 파일을 수정하면 하루 안에 이 페이지에
반영됩니다. 이 저장소를 건드릴 필요가 없습니다.

[data]: https://github.com/JBNU-CILAB/JBNU-CILAB.github.io/tree/main/_data

| 페이지 섹션 | 원본 파일 |
| --- | --- |
| 제목 · 소속 · 지도교수 | `_config.yml`, `_data/professor.yml` |
| 연구 분야 | `_data/research.yml` |
| 프로젝트 | `_data/projects.yml` |
| 연구실 소식 | `_data/news.yml` |
| 주요 논문 | `_data/publications.yml` |
| 멤버 활동 | `_data/members.yml` |

소개 문구, 상단 링크처럼 홈페이지에 대응하는 데이터가 없는 부분은
`profile/README.template.md` 의 마커 바깥을 직접 수정하면 됩니다.

## 로컬에서 실행하기

```sh
pip install -r scripts/requirements.txt
GITHUB_TOKEN="$(gh auth token)" REFRESH_ACTIVITY=true python scripts/build_profile.py
```

`REFRESH_ACTIVITY=false` 로 두면 API 를 호출하지 않고 캐시된 활동 데이터로
렌더링합니다.
