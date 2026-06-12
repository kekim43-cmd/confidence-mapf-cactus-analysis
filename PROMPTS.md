# AI Coding Tool 프롬프트 로그 (PROMPTS.md)

## 개요

| 항목 | 내용 |
|---|---|
| 과제 | AI Coding Tools을 이용하여 타겟논문의 "실험" 파트(공개 구현체)를 구현·실행·분석 |
| 대상 논문 | Confidence-Based Curriculum Learning for Multi-Agent Path Finding (AAMAS 2024) |
| 대상 오픈소스 | <https://github.com/thomyphan/rl4mapf> |
| 사용 도구 | OpenAI Codex CLI |
| 작업 일자 | 2026-05-05 |
| 산출 저장소 | <https://github.com/kekim43-cmd/confidence-mapf-cactus-analysis> |

아래는 실험 구현 과정에서 AI 코딩 툴에 단계별로 지시한 내용을 정리한 프롬프트 로그이다. 각 프롬프트 아래에 AI가 수행한 내용과 산출물을 함께 기록했다.

---

## 구현 및 실행 프롬프트 로그

### 1. 저장소 클론 및 구조 파악

> Confidence-Based Curriculum Learning for Multi-Agent Path Finding 논문의 공개 구현체 thomyphan/rl4mapf를 작업 폴더에 클론하고, 저장소 구조랑 실행 진입점이 어디인지 파악해줘.

**수행 내용**: `git clone https://github.com/thomyphan/rl4mapf.git` 실행 후 구조 분석. 실행 진입점은 `run_training.py`(학습)와 `eval.py`(평가)이고, 핵심 로직은 `cactus/` 패키지(algorithms, curriculum, experiments, env, controller, modules)에 있음을 확인.

### 2. 원본 실행 규모 평가

> run_training.py를 기본 설정 그대로 돌리면 어느 정도 규모야? 일반 노트북에서 바로 재현할 수 있는 수준인지 판단해줘. eval.py도 바로 돌릴 수 있는지 봐줘.

**수행 내용**: `run_training.py` 기본값이 5000 epochs × 32 episodes에 PPO_QMIX/QPLEX/MAPPO × CACTUS/Random, PRIMAL 등 7개 실험 조합을 연속 실행하는 장시간 실험용임을 확인. `eval.py`는 저장소에 포함되지 않은 PRIMAL test map `.npy`를 요구하므로 즉시 실행 불가. 이에 따라 "전체 재현 대신 학습 경로가 끝까지 도는지 검증하는 최소 실행(smoke test)"으로 범위를 정함.

### 3. 의존성 도출 및 가상환경 구성

> 원본 저장소에 requirements.txt가 없네. 코드의 import 문을 역추적해서 실행에 필요한 최소 의존성을 뽑아서 requirements.txt로 만들고, 프로젝트 전용 가상환경(.venv)을 구성해서 설치해줘.

**수행 내용**: import 역추적으로 최소 의존성(torch, numpy, pygame) 도출 → `requirements.txt` 작성. 작업 환경 PATH에 python이 없어 가상환경을 만들고 이후 모든 실행을 `.\.venv\Scripts\python.exe` 절대 경로 호출로 통일. 설치 버전: Python 3.12.13, torch 2.11.0+cpu, numpy 2.4.4, pygame 2.6.1.

### 4. smoke test 스크립트 작성

> 원본 코드는 한 줄도 수정하지 말고, 같은 모듈을 import해서 PPO_QMIX + CACTUS curriculum 조합으로 학습 루프를 한 번 끝까지 통과시키는 smoke test 스크립트를 만들어줘. agent 2개, 6×6 맵, 2 epochs 정도로 아주 작게 잡고, 재현되게 seed를 고정해. 실행 설정이랑 결과는 JSON으로 자동 저장되게 해줘.

**수행 내용**: `scripts/run_cactus_smoke.py` 작성. `sys.path`에 원본 저장소를 추가하고 `cactus.algorithms`, `cactus.env.env_generator`, `cactus.experiments`를 그대로 import. 파라미터는 PPO_QMIX + CACTUS, 2 agents, map size 6, 2 epochs, episodes per epoch 1, time limit 12, hidden dim 16, seed 7. 실행 환경·파라미터·결과를 `run_summary.json`으로 저장하는 로직 포함.

### 5. 실행 및 결과 검증

> 스크립트 실행해서 환경 생성 → CACTUS curriculum 초기화 → rollout → 학습 update → 결과 저장까지 끊김 없이 도는지 확인하고, 생성된 파일들을 정리해줘.

**수행 내용**: 실행 성공 (elapsed 약 0.608초, training total 약 0.385초). `cactus_smoke_output/quick-run-20260505-162050/` 아래에 `results.json`, `run_summary.json`, `actor_net.pth`, `critic_net.pth`, `mixer_net.pth` 생성 확인. success_rate/completion_rate 0.0은 극소 설정의 무작위 초기 학습이므로 성능이 아닌 실행 경로 검증 결과로 해석.

### 6. 실행 경고 원인 분석 및 패치 제안

> 실행 중에 "parameters is an empty generator, no gradient clipping will occur" 경고가 떴어. 원인을 코드 레벨에서 분석해줘. 원본을 직접 고치지는 말고, 수정 제안을 패치(diff) 형태로 따로 정리해.

**수행 내용**: `cactus/controller/a2c_controller.py`에서 `parameters()` generator를 변수에 저장한 뒤 optimizer 생성에서 소비하고 gradient clipping에 재사용하는 것이 원인임을 분석. generator를 `list()`로 보관하는 수정안을 `patches/recommended_patch_policy_parameters.diff`로 작성 (원본 무수정 유지).

### 7. 코드-논문 대응 분석 및 분석 보고서 작성

> 지금까지 본 코드 구조를 논문 개념이랑 대응시켜서 정리해줘. 할당 반경, 신뢰도 기반 진급 조건, 반경 내 목표 샘플링이 코드 어디에 구현돼 있는지 확인하고, 실행 결과까지 포함해서 분석 보고서로 만들어줘.

**수행 내용**: 논문 개념과 코드의 대응 확인 — 할당 반경 `CACTUSCurriculum.radius`, 진급 조건 `mean - deviation_factor * stddev >= improvement_threshold`(논문의 μ − ησ ≥ U), 반경 내 목표 샘플링 `GridWorld.reset()`. `density=0`이어도 장애물이 생성되는 `env_generator.py`의 동작 등 구현상 특이점 포함. 결과를 `analysis/cactus_source_analysis_report.md`로 작성.

---

## 프롬프트 활용 방식 정리

이번 과제에서 AI Coding Tool에 프롬프트를 입력한 방식은 다음과 같이 요약된다.

1. **구현 전에 실행 규모부터 평가시켰다** — 코드를 받자마자 돌리지 않고, 원본 기본 설정의 규모와 즉시 실행 가능 여부를 먼저 판단하게 한 뒤 smoke test로 범위를 정했다.
2. **원본 무수정 원칙을 프롬프트에 명시했다** — "원본 코드는 한 줄도 수정하지 말고 import만 해라"를 지시에 포함해, 검증 결과가 원본 코드 자체의 동작임을 보장했다.
3. **실행 파라미터와 재현 조건을 직접 지정했다** — agent 수, 맵 크기, epoch 수, seed 고정, 결과 JSON 자동 저장까지 프롬프트에서 명시해 누구나 같은 결과를 재현할 수 있게 했다.
4. **경고는 해결로 끝내지 않고 원인 분석과 패치 제안까지 시켰다** — gradient clipping 경고를 코드 레벨에서 분석하게 하고, 원본 수정 대신 diff 형태의 권장 패치로 정리하게 했다.
