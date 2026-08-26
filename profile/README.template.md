<!--
  =============================================================================
  이 파일이 조직 프로필 페이지의 원본입니다. 직접 편집하는 파일은 이쪽입니다.

  AUTO:<이름>:START / AUTO:<이름>:END 마커 안쪽만 update-profile 워크플로가
  자동으로 생성합니다. 그 바깥은 전부 수기로 관리하며 그대로 보존됩니다.

  profile/README.md 는 생성물이므로 직접 편집하지 마세요. 덮어써집니다.

  (주의: 이 블록 안에 주석 종료 기호가 들어가면 주석이 거기서 끊겨
   나머지 내용이 공개 페이지에 그대로 노출됩니다.)
  =============================================================================
-->

# Compiler Intelligence Lab (CILAB)

**Jeonbuk National University** · Division of Computer Science and Artificial Intelligence

We study how code runs, and how to make it run faster — across web engines,
LLM-based systems, and AI compilers. The work is empirical: we profile real
engines, find the bottlenecks, and upstream the fixes.

[cilab.jbnu.ac.kr](https://cilab.jbnu.ac.kr)

## Projects

**Open source we contribute to**

| Project | Description |
| --- | --- |
| [**Escargot**](https://github.com/Samsung/escargot) | Lightweight JavaScript engine for memory-constrained devices, supporting modern ECMAScript in a small footprint. We analyze its internals and work on performance and memory optimizations. |
| [**Walrus**](https://github.com/Samsung/walrus) | Lightweight WebAssembly runtime with full standard support, built around an interpreter with JIT compilation underway. We work on execution performance. |
| [**lwnode**](https://github.com/Samsung/lwnode) | Memory-efficient Node.js implementation running on top of Escargot, targeting consumer devices such as phones, watches, and TVs. |

**Built in the lab**

| Project | Description |
| --- | --- |
| [**Escargot Review Bot**](https://github.com/JBNU-CILAB/escargot-review-bot) | Self-hosted AI reviewer for Escargot pull requests. Four LLM passes — defect, refactoring, compiler, and style — feed a judge stage that merges overlapping findings into inline comments, running entirely on a local LLM. |
| [**JCodeQuest**](https://github.com/JBNU-CILAB/JCodeQuest) | Gamified platform for algorithm practice, with LLM-generated problems, three-judge ensemble grading, real-time code battles, and automatic plagiarism checks. |
| [**demucs-lite**](https://github.com/JBNU-CILAB/demucs-lite) | Compressing the Demucs source-separation model to run on mobile. FP16/INT8 quantization and audio chunking bring inference for one second of audio to roughly 100 ms on a Qualcomm NPU. |
| **Iron Device Simulator** <br><sub>private</sub> | Web dashboard for a speaker protection library, visualizing speaker temperature and diaphragm displacement in real time from audio files or live microphone input. Built as an industry collaboration project. |

## Member Activity

<!-- AUTO:ACTIVITY:START -->
<!-- AUTO:ACTIVITY:END -->
