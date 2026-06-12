# CACTUS 오픈소스 코드 실행 결과 보고서

## 1. 실행 목적

본 보고서는 논문 **Confidence-Based Curriculum Learning for Multi-Agent Path Finding**의 공개 GitHub 구현체가 실제로 실행 가능한지 확인한 결과를 정리한 것이다.

이번 실행은 논문 전체 성능을 재현하는 full training이 아니라, 공개 코드가 다음 경로까지 정상 동작하는지 확인하는 **smoke test**이다.

본 과제는 AI Coding Tools을 이용하여 논문의 "실험" 파트를 구현하는 과제로, 구현 전 과정은 **OpenAI Codex CLI**를 통해 진행하였다. 단계별 구현 과정은 3장, 입력한 프롬프트는 4장과 [PROMPTS.md](PROMPTS.md)에 정리하였다.

![실행 검증 파이프라인](assets/execution_pipeline.png)

## 2. 내가 실행한 것

대상 공개 코드:

- 원본 저장소: <https://github.com/thomyphan/rl4mapf>
- 본 보고서 저장소: <https://github.com/kekim43-cmd/confidence-mapf-cactus-analysis>

내가 실행한 스크립트:

```powershell
.\.venv\Scripts\python.exe .\scripts\run_cactus_smoke.py
```

실행 설정:

| 항목 | 값 |
|---|---|
| 알고리즘 | PPO_QMIX |
| Curriculum | CACTUS |
| Agent 수 | 2 |
| Epoch 수 | 2 |
| Episodes per epoch | 1 |
| Map size | 6 |
| Time limit | 12 |
| 목적 | 논문 전체 재현이 아닌 최소 실행 경로 검증 |

## 3. 순차적 구현 매뉴얼

AI Coding Tool(OpenAI Codex CLI)을 이용해 실제로 진행한 순서를 단계별로 정리한 것이다. 동일한 순서로 따라 하면 같은 결과를 얻을 수 있다.

### 1단계. 오픈소스 공개 여부 확인

구현에 앞서 논문의 공개 코드가 실제로 존재하고 사용 가능한지 확인하였다.

- 저자 공식 페이지의 `[code]` 링크가 public 저장소 `thomyphan/rl4mapf`로 연결됨
- Springer 확장 논문의 Code availability에도 같은 저장소가 명시됨
- 라이선스: 연구·교육 목적 사용 가능 (상업적 사용은 별도 문의 필요)
- 확인 내용은 `analysis/cactus_open_source_check.md`에 기록

### 2단계. 원본 저장소 클론

```powershell
git clone https://github.com/thomyphan/rl4mapf.git rl4mapf
```

### 3단계. 코드 구조 파악

클론한 코드를 분석하여 실행 진입점과 제약을 파악하였다.

| 구성 요소 | 내용 |
|---|---|
| `run_training.py` | 논문 실험용 학습 스크립트. 기본값이 5000 epochs × 여러 알고리즘 조합이라 그대로 돌리기엔 장시간 필요 |
| `eval.py` | 평가 스크립트. 저장소에 포함되지 않은 PRIMAL test map `.npy` 파일을 요구 |
| `cactus/` | 핵심 모듈 — `algorithms`(PPO_QMIX 등 controller), `env/env_generator`(MAPF 그리드월드 생성), `experiments`(학습 루프) |
| `requirements.txt` | 원본에 없음 → 코드의 import를 역추적해 의존성 도출 필요 |

### 4단계. 실행 환경 구성

원본에 requirements.txt가 없어 import 역추적으로 의존성(torch, numpy, pygame)을 확인하고, 가상환경을 구성하였다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 5단계. smoke test 스크립트 작성

원본 `run_training.py`는 즉시 재현용으로는 규모가 너무 크기 때문에, **원본 코드를 한 줄도 수정하지 않고** 같은 모듈을 import하여 아주 작은 설정으로 학습 루프를 한 번 통과시키는 `scripts/run_cactus_smoke.py`를 작성하였다.

- `sys.path`에 원본 저장소를 추가하고 `cactus.algorithms`, `cactus.env.env_generator`, `cactus.experiments`를 import
- 축소 파라미터: PPO_QMIX + CACTUS curriculum, 2 agents, 6×6 map, 2 epochs, time limit 12, hidden dim 16
- 재현성을 위해 random / numpy / torch seed 고정 (seed=7)
- 실행 결과를 `run_summary.json`으로 자동 저장

### 6단계. 실행 및 결과 확인

```powershell
.\.venv\Scripts\python.exe .\scripts\run_cactus_smoke.py
```

실행 결과 `cactus_smoke_output/quick-run-20260505-162050/` 아래에 `results.json`, `run_summary.json`, 가중치 3종이 생성됨을 확인하였다 (상세 결과는 5장).

### 7단계. 소스 분석 및 발견점 정리

- 소스 구조·알고리즘 구현 분석: `analysis/cactus_source_analysis_report.md`
- 실행 중 발견한 gradient clipping 경고에 대한 권장 패치: `patches/recommended_patch_policy_parameters.diff`

### 8단계. GitHub 업로드

본인 계정에 public 저장소를 생성하고 산출물을 업로드하였다.

- 2026-05-05: 분석·smoke test 일체 업로드 (`Add CACTUS MAPF analysis and smoke test`)
- 2026-05-13: 실행 결과 화면 캡처와 본 보고서 추가 (`Add execution report with result screenshots`)

## 4. 프롬프트 입력 내용

실험 구현의 각 단계는 OpenAI Codex CLI에 단계별 프롬프트를 입력하여 진행하였다. 단계별 지시 내용의 요지는 다음과 같으며, 수행 내용을 포함한 전체 로그는 [PROMPTS.md](PROMPTS.md)에 있다.

| 단계 | 지시 내용 |
|---|---|
| 클론·구조 파악 | rl4mapf 저장소를 클론하고 저장소 구조와 실행 진입점을 파악 |
| 실행 규모 평가 | run_training.py 기본 설정의 규모와 즉시 재현 가능 여부를 판단 |
| 의존성·환경 구성 | import 역추적으로 최소 의존성을 도출해 requirements.txt 작성, 가상환경 구성 |
| smoke 스크립트 작성 | 원본 무수정·import 방식으로 PPO_QMIX + CACTUS 최소 학습 루프 스크립트 작성 (2 agents, 6×6, 2 epochs, seed 고정, 결과 JSON 저장) |
| 실행·검증 | 환경 생성부터 결과 저장까지 전체 경로 통과 확인, 산출물 정리 |
| 경고 분석·패치 | gradient clipping 경고의 원인을 코드 레벨에서 분석하고 권장 패치 diff 작성 |
| 분석 보고서 | 논문 개념과 코드 구현의 대응 관계를 확인해 분석 보고서 작성 |

## 5. 실행 결과 화면

아래 이미지는 로컬에서 실행한 결과 화면을 보고서용으로 정리한 것이다.

![실행 결과 화면](assets/terminal_result_capture.png)

실행 결과 요약:

| 항목 | 결과 |
|---|---|
| 전체 elapsed time | 0.608초 |
| training total time | 0.385초 |
| success_rate | `[0.0, 0.0, 0.0]` |
| completion_rate | `[0.0, 0.0, 0.0]` |
| 생성 결과 파일 | `results.json`, `run_summary.json`, `actor_net.pth`, `critic_net.pth`, `mixer_net.pth` |

![Smoke Run 실행 결과 요약](assets/smoke_run_dashboard.png)

`success_rate`와 `completion_rate`가 0으로 나온 것은 성능 실패를 의미하지 않는다. 이번 실행은 2 agents, 2 epochs의 매우 짧은 smoke run이므로, 학습 성능을 평가하기 위한 실험이 아니다. 이 결과는 공개 코드가 환경 생성, rollout, 학습 update, 결과 저장 단계까지 정상적으로 실행되는지를 확인한 값이다.

## 6. 생성된 산출물

실행 후 다음 파일이 생성되는 것을 확인하였다.

| 파일 | 의미 |
|---|---|
| `results.json` | success rate, completion rate, training time 저장 |
| `run_summary.json` | 실행 환경, 파라미터, 결과 요약 |
| `actor_net.pth` | policy actor 가중치 |
| `critic_net.pth` | critic network 가중치 |
| `mixer_net.pth` | QMIX mixing network 가중치 |

![생성 산출물 및 재현 가능성](assets/artifacts_reproducibility.png)

## 7. 직접 실행하는 방법

Windows PowerShell 기준 실행 방법은 다음과 같다.

```powershell
git clone https://github.com/kekim43-cmd/confidence-mapf-cactus-analysis.git
cd confidence-mapf-cactus-analysis

git clone https://github.com/thomyphan/rl4mapf.git rl4mapf

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\scripts\run_cactus_smoke.py
```

macOS/Linux 환경에서는 마지막 두 줄을 다음처럼 바꾸면 된다.

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python ./scripts/run_cactus_smoke.py
```

실행이 성공하면 `cactus_smoke_output/quick-run-.../` 폴더 아래에 다음 파일들이 생성된다.

```text
results.json
run_summary.json
actor_net.pth
critic_net.pth
mixer_net.pth
```

## 8. 실행 환경

내가 실행한 환경은 다음과 같다.

| 항목 | 버전 |
|---|---|
| Python | 3.12.13 |
| PyTorch | 2.11.0+cpu |
| NumPy | 2.4.4 |
| pygame | 2.6.1 |

## 9. 주의할 점

원본 저장소의 `run_training.py`는 논문 실험용 장시간 학습 스크립트이다. 기본 설정은 5000 epochs와 여러 알고리즘 조합을 순차 실행하므로, 일반 노트북에서 바로 돌리기에는 시간이 오래 걸린다.

또한 원본 `eval.py`는 PRIMAL test map `.npy` 파일을 요구한다. 이 파일은 원본 GitHub 저장소에 포함되어 있지 않으므로, 논문 평가 결과 전체를 그대로 재현하려면 별도 테스트 맵 자료를 받아 `instances/primal_test_envs`에 배치해야 한다.

## 10. 프로젝트와의 연결

이 논문은 스마트팩토리 MCS-RTD 통합 제어 플랫폼의 **AI 경로 최적화 모듈**과 직접적으로 연결된다.

- RTD 룰 빌더: 작업 우선순위와 목표 할당 조건을 생성
- MCS 반송 제어: agent 위치, 충돌 제약, 실행 명령을 관리
- CACTUS/MARL: 시뮬레이션에서 동적 경로 정책을 학습
- 통합 대시보드: completion, congestion, collision risk를 모니터링

![프로젝트 적용 관점 요약](assets/project_link_summary.png)

## 11. 결론

이번 실험은 논문 전체 성능 재현이 아니라 공개 구현체의 실행 가능성 검증을 목표로 수행하였다. 최소 설정의 smoke run을 통해 CACTUS curriculum, PPO_QMIX controller, MAPF 환경 rollout, 학습 update, 결과 및 가중치 저장이 정상적으로 이어지는 것을 확인하였다.

따라서 해당 오픈소스는 프로젝트의 AI 경로 최적화 모듈을 설계하고 분석하는 출발점으로 활용 가능하다.
