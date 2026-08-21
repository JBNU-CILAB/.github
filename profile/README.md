<!--
  =============================================================================
  이 파일이 조직 프로필 페이지의 원본입니다. 직접 편집하는 파일은 이쪽입니다.

  AUTO:<이름>:START / AUTO:<이름>:END 마커 바깥은 자유롭게 수정할 수 있으며
  그대로 보존됩니다. 마커 안쪽은 JBNU-CILAB.github.io/_data 의 내용으로
  update-profile 워크플로가 매번 다시 생성합니다.

  profile/README.md 는 생성물이므로 직접 편집하지 마세요. 덮어써집니다.

  (주의: 이 블록 안에 주석 종료 기호가 들어가면 주석이 거기서 끊겨
   나머지 내용이 공개 페이지에 그대로 노출됩니다.)
  =============================================================================
-->

<!-- AUTO:HEADER:START -->
# 컴파일러 인텔리전스 연구실

**Compiler Intelligence Lab (CILAB)**

전북대학교 컴퓨터인공지능학부

지도교수 · [박혁우](https://github.com/clover2123) 조교수
<!-- AUTO:HEADER:END -->

코드가 어떻게 실행되는지, 그리고 어떻게 하면 더 빠르게 실행할 수 있는지를
연구합니다. 실제로 널리 쓰이는 엔진을 직접 프로파일링해 병목을 찾고, 개선한
결과가 실사용 코드에 반영되도록 하는 실증적 접근을 지향합니다.

[홈페이지](https://cilab.jbnu.ac.kr) · [구성원](https://cilab.jbnu.ac.kr/people/) · [연락처](https://cilab.jbnu.ac.kr/contact/)

---

## 연구 분야

<!-- AUTO:RESEARCH:START -->
### [🌐 웹 엔진](https://cilab.jbnu.ac.kr/research/#web-engines)

웹 브라우저의 핵심 실행 환경인 자바스크립트 엔진과 웹어셈블리(WebAssembly) 엔진을 분석하고, 실행 성능을 높이기 위한 최적화 기법을 연구합니다.

`JavaScript 엔진` `WebAssembly` `JIT 컴파일` `메모리 최적화` `성능 프로파일링` `오픈소스`

### [🤖 LLM 응용 시스템](https://cilab.jbnu.ac.kr/research/#llm-system)

오픈 웨이트(open-weight) LLM을 활용하여 다양한 작업을 자동화하는 지능형 시스템을 설계하고 구축하는 연구를 수행합니다.

`Open-weight LLM` `프롬프트 엔지니어링` `Tool Use` `LLM 에이전트` `자동화 시스템`

### [🧠 AI 컴파일러](https://cilab.jbnu.ac.kr/research/#ai-compiler)

딥러닝 모델이 다양한 하드웨어에서 효율적으로 실행되도록 컴파일 및 최적화하는 기술을 연구합니다.

`딥러닝 컴파일러` `중간 표현(IR)` `그래프 최적화` `코드 생성` `오토튜닝`
<!-- AUTO:RESEARCH:END -->

## 프로젝트

<!-- AUTO:PROJECTS:START -->
**참여 오픈소스 프로젝트**

| 프로젝트 | 설명 | 저장소 |
| --- | --- | --- |
| **Escargot** | 경량 자바스크립트 엔진 | [`Samsung/escargot`](https://github.com/Samsung/escargot) |
| **Walrus** | 경량 웹어셈블리 런타임 | [`Samsung/walrus`](https://github.com/Samsung/walrus) |
| **lwnode** | 경량 Node.js | [`Samsung/lwnode`](https://github.com/Samsung/lwnode) |

**자체 개발 프로젝트**

| 프로젝트 | 설명 | 저장소 |
| --- | --- | --- |
| **Escargot Review Bot** | LLM 기반 코드 리뷰 시스템 | [`JBNU-CILAB/escargot-review-bot`](https://github.com/JBNU-CILAB/escargot-review-bot) |
| **JCodeQuest** | LLM 기반 코딩 학습 플랫폼 | [`JBNU-CILAB/JCodeQuest`](https://github.com/JBNU-CILAB/JCodeQuest) |
| **Iron Device Simulator** | 스피커 보호 알고리즘 시뮬레이터 | [`JBNU-CILAB/Iron-Device-Simulator`](https://github.com/JBNU-CILAB/Iron-Device-Simulator) |
| **demucs-lite** | 음원 분리 모델 경량화 | [`JBNU-CILAB/demucs-lite`](https://github.com/JBNU-CILAB/demucs-lite) |
<!-- AUTO:PROJECTS:END -->

## 연구실 소식

<!-- AUTO:NEWS:START -->
- **2026.07–08** 💼 인턴 — 권순범, 권민석 학생 아이언디바이스 인턴십 수행
- **2026.07** 👋 신입 — 김현준, 유인상 학생 연구실 합류
- **2026.06** 🏆 수상 — 양현성 학생, 한국컴퓨터종합학술대회(KCC 2026) 우수논문상 수상
  <br>논문: Native Stack 기반 웹어셈블리 인터프리터에서의 Tail Call Optimization 설계 및 구현
- **2026.06** 📢 학회 — 권순범, 권민석, 박현명, 양현성 학생 한국컴퓨터종합학술대회(KCC 2026) 참석
  <br>권민석, 양현성 학생 논문 발표
- **2026.04** 👋 신입 — 박현명, 양현성 학생 연구실 합류

[전체 소식 보기 →](https://cilab.jbnu.ac.kr/news/)
<!-- AUTO:NEWS:END -->

## 최근 논문

<!-- AUTO:PUBLICATIONS:START -->
- **[Native Stack 기반 웹어셈블리 인터프리터에서의 Tail Call Optimization 설계 및 구현](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE12929755)** 🏆 우수논문상
  <br>**양현성** and **박혁우** — 한국정보과학회 2026 한국컴퓨터종합학술대회 논문집 (KCC 2026), pp. 1646–1648, Jun. 2026
- **[실시간 오디오 기반 스피커 분석 시스템의 저지연 시각화를 위한 출력 큐 병합 기법](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE12929407)**
  <br>**권민석** and **박혁우** — 한국정보과학회 2026 한국컴퓨터종합학술대회 논문집 (KCC 2026), pp. 636–638, Jun. 2026
- **[듀얼 패스 프롬프트와 후처리 필터링을 이용한 고품질 JS 엔진 코드 리뷰 시스템](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE12577935)**
  <br>**이재헌** and **박혁우** — 한국정보과학회 2025 한국소프트웨어종합학술대회 논문집 (KSC 2025), pp. 1485–1487, Dec. 2025
- **[미사용 함수 파라미터 제거를 활용한 자바스크립트 엔진 최적화](https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE12577711)**
  <br>**권순범** and **박혁우** — 한국정보과학회 2025 한국소프트웨어종합학술대회 논문집 (KSC 2025), pp. 1049–1051, Dec. 2025
- **[Tail Call Optimization Tailored for Native Stack Utilization in JavaScript Runtimes](https://doi.org/10.1109/access.2024.3441750)**
  <br>**Hyukwoo Park** and Seonghyun Kim — IEEE Access, vol. 12, pp. 111801–111817, Aug. 2024

[전체 논문 목록 →](https://cilab.jbnu.ac.kr/publication/)
<!-- AUTO:PUBLICATIONS:END -->

## 멤버 활동

<!-- AUTO:ACTIVITY:START -->
> 2026년 1월 1일부터 집계한 연구실·오픈소스 프로젝트 저장소 공개 기여 내역입니다. 비공개 저장소와 비공개 기여는 집계에서 제외됩니다.

| 멤버 | 활동 저장소 |
| --- | --- |
| [권순범](https://github.com/kwonjeomsim) | [`Samsung/escargot`](https://github.com/Samsung/escargot), [`Samsung/walrus`](https://github.com/Samsung/walrus), [`JBNU-CILAB/escargot`](https://github.com/JBNU-CILAB/escargot), [`JBNU-CILAB/walrus`](https://github.com/JBNU-CILAB/walrus) |
| [권민석](https://github.com/M-SE0K) | [`JBNU-CILAB/JCodeQuest`](https://github.com/JBNU-CILAB/JCodeQuest), [`JBNU-CILAB/escargot-review-bot`](https://github.com/JBNU-CILAB/escargot-review-bot), [`Samsung/walrus`](https://github.com/Samsung/walrus) |
| [박현명](https://github.com/comts224) | [`JBNU-CILAB/JCodeQuest`](https://github.com/JBNU-CILAB/JCodeQuest) |
| [양현성](https://github.com/makachanm) | [`JBNU-CILAB/JCodeQuest`](https://github.com/JBNU-CILAB/JCodeQuest), [`Samsung/walrus`](https://github.com/Samsung/walrus) |
| [김현준](https://github.com/hyraxbyerax) | [`Samsung/walrus`](https://github.com/Samsung/walrus) |
| [유인상](https://github.com/Luca388) | [`Samsung/walrus`](https://github.com/Samsung/walrus) |

2026년 연구실 전체 — 공개 저장소 **6**곳에 커밋 **221**건, Pull Request **42**건.
<!-- AUTO:ACTIVITY:END -->
