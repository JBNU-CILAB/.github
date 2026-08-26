# JBNU-CILAB/.github

<https://github.com/JBNU-CILAB> 조직 첫 화면에 표시되는 프로필 페이지를 관리하는
저장소입니다.

페이지 대부분은 [`profile/README.template.md`](profile/README.template.md) 에서
수기로 관리합니다. 자동으로 생성되는 부분은 **멤버 활동 섹션 하나**뿐이며, 이를
위해 홈페이지 저장소인 [JBNU-CILAB.github.io][site] 에서 두 파일만 읽습니다.

[site]: https://github.com/JBNU-CILAB/JBNU-CILAB.github.io

| 읽는 파일 | 용도 |
| --- | --- |
| `_data/members.yml` | 활동 연동에 동의한 멤버의 GitHub 계정 |
| `_data/projects.yml` | 연구실 저장소 판별용 목록 (활동 집계 범위) |

소개 문구와 프로젝트 표는 홈페이지에 대응하는 영문 데이터가 없어 템플릿에서 직접
관리합니다. 프로젝트가 추가·변경되면 템플릿의 표를 함께 고쳐 주세요.

## 구성

| 경로 | 역할 |
| --- | --- |
| `profile/README.template.md` | 직접 편집하는 원본. 소개·프로젝트 + `AUTO:ACTIVITY` 마커. |
| `profile/README.md` | **생성물.** 직접 편집하지 마세요, 덮어써집니다. |
| `scripts/build_profile.py` | 멤버 활동 수집 및 렌더러. |
| `data/activity-cache.json` | **생성물.** 마지막 멤버 활동 데이터 (폴백용). |
| `.github/workflows/update-profile.yml` | 스케줄러. |

## 동작 방식

홈페이지 저장소는 데이터가 바뀌어도 이 저장소에 알려줄 수 없습니다. 그래서 세 개의
트리거로 동작합니다.

- **push** — `profile/README.template.md` 나 `scripts/build_profile.py` 를 수정해
  푸시하면 즉시 다시 렌더링합니다. 활동은 캐시를 그대로 씁니다.
- **매주 월요일 06:30 KST** — 멤버 활동을 갱신합니다.
- **`workflow_dispatch`** — 수동 실행. 기본값으로 활동까지 갱신합니다.

활동 갱신을 주 1회만 돌리는 데에는 이유가 있습니다. 기여 수치는 멤버가 커밋하는
것만으로 저절로 변하기 때문에, 더 자주 갱신하면 편집상 의미가 없는 봇 커밋이
쌓입니다.

집계 연도는 실행 시점을 기준으로 자동으로 넘어갑니다. 2027년 1월 1일이 되면 별도
설정 없이 2027년 1월 1일부터의 기여를 집계합니다. 캐시가 지난해 집계로 남아 있으면
트리거와 무관하게 활동을 갱신합니다.

활동 수집은 실패가 허용됩니다. 오류가 나면 `data/activity-cache.json` 의 직전
결과를 다시 읽어오므로 섹션이 조용히 비워지는 일은 없습니다.

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
- **실명과 이메일은 출력하지 않습니다.** 표에는 GitHub 계정만 표시됩니다.
  조직 프로필은 크롤러가 수집해 가는 공개 페이지입니다.

## 로컬에서 실행하기

```sh
pip install -r scripts/requirements.txt
GITHUB_TOKEN="$(gh auth token)" REFRESH_ACTIVITY=true python scripts/build_profile.py
```

`REFRESH_ACTIVITY=false` 로 두면 API 를 호출하지 않고 캐시된 활동 데이터로
렌더링합니다.
