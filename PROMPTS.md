# AI Coding Tool 프롬프트 로그 (PROMPTS.md)

## 개요

| 항목 | 내용 |
|---|---|
| 과제 | AI Coding Tools을 이용하여 타겟논문의 "실험" 파트(공개 구현체)를 실행·분석 |
| 대상 논문 | Confidence-Based Curriculum Learning for Multi-Agent Path Finding |
| 대상 오픈소스 | <https://github.com/thomyphan/rl4mapf> |
| 주 사용 도구 | OpenAI Codex CLI — 코드 구현·실행·GitHub 업로드·보고서 작성 |
| 보조 도구 | Claude Code — 논문 선정 및 오픈소스 사전 조사 |
| 작업 일자 | 2026-05-05 (구현·실행·업로드), 2026-05-13 (실행 결과 보고서) |
| 산출 저장소 | <https://github.com/kekim43-cmd/confidence-mapf-cactus-analysis> |

아래 프롬프트는 AI 도구가 로컬에 저장한 세션 기록(Codex CLI의 `~/.codex/sessions/` rollout 파일, Claude Code의 `~/.claude/history.jsonl`)에서 **실제 입력한 원문을 그대로** 시간순으로 발췌한 것이다. 각 프롬프트 아래에 AI가 수행한 내용을 정리했다.

---

## 0단계. 사전 조사 — 논문 선정과 오픈소스 확인 (Claude Code, 2026-03-22 ~ 03-24)

**[03-22 01:18]**

> 내가 스마트팩토리캡스톤디자인 이라는 수업에서 들으려고 하는 수업에서 타겟논문을 3편을 선정해서 골라야해. 내가 이 수업에서 진행하는 프로젝트는 @smartfactory\RTD_MCS_소개.pdf @smartfactory\연구개발_프로젝트_신청서_김경호_260215.pdf 이 두 pdf에 설명되어 있어. (…) 최대한 오픈소스가 함께 있는 논문 3편을 찾아줘. 이 3편 중에 우리의 주제에 가장 fit한 애를 찾아줘

**[03-22 03:24]**

> 각 논문 3개에 해당하는 오픈소스가 뭔지도 알아봐줘

**[03-24 01:42]**

> smartfactory 디렉토리 안에 있는 프로젝트를 할거야. 타겟논문 3편 중에 @"smartfactory\3. Confidence-Based Curriculum Learning for Multi-Agent Path Finding.pdf" 를 선정했어. (…)

→ AI 수행 내용: 프로젝트 신청서(MCS-RTD 통합 제어 플랫폼)와 연관된 오픈소스 동반 논문 후보를 조사하고, 각 후보의 공개 코드 저장소를 확인. 최종적으로 CACTUS 논문을 타겟으로 선정.

---

## 1단계. 작업 환경 준비 및 오픈소스 공개 여부 재확인 (Codex CLI, 2026-05-05)

**[05-05 15:59]**

> 여기 안의 2. smartfactory 라는 디렉토리 안에서 5/5 디렉토리 만들어서 여기 안에다가 저장하자 앞으로 하는거

**[05-05 15:59]**

> Confidence-Based Curriculum Learning for Multi-Agent Path Finding 이 논문이 오픈소스가 있어서 오픈소스 코드 구현 및 분석을 할 수 있다고 했었는데 다시 확인해봐

→ AI 수행 내용: 작업 폴더 생성 후, 저자 공식 페이지의 `[code]` 링크 → `thomyphan/rl4mapf` public 저장소, Springer 확장 논문의 Code availability까지 교차 확인. 라이선스(연구·교육 목적 사용 가능, 상업적 사용은 별도 문의)와 주의점(requirements.txt 부재, PRIMAL 테스트 맵 별도 필요)을 정리해 `analysis/cactus_open_source_check.md`로 저장.

---

## 2단계. 구현 및 실행 (Codex CLI, 2026-05-05)

**[05-05 16:09]**

> 한번 해보자

**[05-05 16:11]**

> 이 논문의 GitHub에 공개되는 오픈소스를 직접 돌려보고 간단히 분석하시고 소스코드/분석보고서를 만들거야.

→ AI 수행 내용:

1. `git clone https://github.com/thomyphan/rl4mapf.git`으로 원본 저장소 확보
2. 코드 구조 분석 — `run_training.py`(기본 5000 epochs), `eval.py`(PRIMAL 테스트 맵 필요), `cactus/` 핵심 모듈(algorithms, env_generator, experiments) 파악
3. requirements.txt가 없어 import 역추적으로 의존성(torch, numpy, pygame) 도출 → `requirements.txt` 작성, 가상환경(`.venv`) 구성
4. 원본 코드를 **수정하지 않고 import만 하는** 최소 실행 스크립트 `scripts/run_cactus_smoke.py` 작성 (PPO_QMIX + CACTUS curriculum, 2 agents, 6×6 map, 2 epochs, seed 고정)
5. 실행 성공 — `results.json`, `run_summary.json`, 가중치 3종(`actor_net.pth`, `critic_net.pth`, `mixer_net.pth`) 생성 확인
6. 소스 분석 보고서(`analysis/cactus_source_analysis_report.md`)와 실행 중 발견한 gradient clipping 경고에 대한 권장 패치(`patches/recommended_patch_policy_parameters.diff`) 작성

---

## 3단계. 본인 GitHub 업로드 (Codex CLI, 2026-05-05)

**[05-05 16:26]**

> 내 깃허브에다가 한 거 아니지?

**[05-05 16:26]**

> 내 깃허브에다가 해줘

**[05-05 16:36]**

> private 말고 링크있으면 볼 수 있게해

→ AI 수행 내용: 본인 계정(`kekim43-cmd`)에 `confidence-mapf-cactus-analysis` 저장소를 생성하고 분석·실행 산출물을 커밋·푸시. 공개 범위를 public으로 전환해 링크만으로 열람 가능하게 설정. (커밋: `Add CACTUS MAPF analysis and smoke test`, 2026-05-05)

---

## 4단계. 실행 결과 보고서 작성 (Codex CLI, 2026-05-13)

**[05-13 14:44]**

> 실행한 결과 보고서에 넣을 사진이나 내용 만들어봐

**[05-13 14:49]**

> github 보고서에 넣을 내용을 적을거야. 내가 무엇을 돌렸고, 그 결과값은 어떻게 나오는지, 교수님이 직접 실행해볼 수 있도록 간단한 설명과 내가 실행한 결과 화면을 캡처해서 올려야해

→ AI 수행 내용: 실행 결과 화면·파이프라인·재현성 정리 이미지(`assets/`) 생성, 실행 명령·결과값·재실행 방법을 담은 `REPORT.md` 작성 후 업로드. (커밋: `Add execution report with result screenshots`, 2026-05-13)

---

## 부록. 연계 작업 프롬프트 (논문 분석 발표자료·Q&A 준비)

실험 구현 외에, 같은 도구로 진행한 연계 작업의 프롬프트 요지는 다음과 같다.

| 일시 | 프롬프트 요지 | 산출물 |
|---|---|---|
| 05-05 16:43 | 분석 보고서를 PPT 템플릿 양식 그대로, 프로젝트 신청서와 연계해 30분 이상 발표 분량으로 제작 요청 | 발표자료 제작 계획 수립 |
| 05-05 16:55 | 수립된 30장 구성 계획 승인 후 일괄 구현 지시 (`PLEASE IMPLEMENT THIS PLAN: …`) | 발표자료 PPTX + 발표대본 + 시간표 |
| 05-19 ~ 05-21 | 발표 스크립트 기반 예상 질문 3개씩 생성, 수집된 질문에 대한 답변 작성 | 발표 Q&A 준비 자료 |

---

## 프롬프트 활용 방식 정리

이번 과제에서 AI Coding Tool에 프롬프트를 입력한 방식은 다음과 같이 요약된다.

1. **사실 확인을 먼저 시킨다** — 구현에 들어가기 전에 "오픈소스가 있는지 다시 확인해봐"로 공개 코드의 존재·라이선스를 검증하게 했다.
2. **목표는 한 문장으로, 판단은 도구에 맡긴다** — "직접 돌려보고 간단히 분석하시고 소스코드/분석보고서를 만들거야" 한 문장으로 클론 → 의존성 구성 → 축소 실행 → 보고서까지 이어지게 했다. 5000 epochs 전체 학습 대신 smoke test로 범위를 줄이는 판단은 도구가 제안했고, 이를 승인했다.
3. **산출물 위치와 공개 범위는 명시적으로 통제한다** — 저장 폴더 고정, 본인 GitHub 업로드, public 전환은 별도 프롬프트로 직접 지시했다.
4. **큰 작업은 계획 승인 후 일괄 실행한다** — 발표자료처럼 산출물이 큰 작업은 먼저 계획을 받아 검토하고, 승인 프롬프트로 한 번에 구현시켰다.
