# Confidence-Based Curriculum Learning for MAPF 코드 실행 및 분석 보고서

작성일: 2026-05-05  
대상 논문: Confidence-Based Curriculum Learning for Multi-Agent Path Finding, AAMAS 2024  
대상 저장소: https://github.com/thomyphan/rl4mapf  
로컬 저장소: `C:\my-project\2. smartfactory\5\5\rl4mapf`  
확인 커밋: `7ca7de6`

## 1. 결론

공개 GitHub 코드는 실제 실행 가능하다. 다만 원본 `run_training.py`는 5000 epoch와 여러 알고리즘 조합을 연속 실행하는 장시간 실험용 스크립트이므로, 이번에는 원본 모듈을 수정하지 않고 별도의 최소 재현 스크립트 `run_cactus_smoke.py`를 작성해 end-to-end 실행을 확인했다.

이번 검증에서 확인한 범위는 다음과 같다.

- 랜덤 MAPF grid 환경 생성
- CACTUS curriculum 초기화
- PPO_QMIX controller 생성
- episode rollout
- policy/critic update 호출
- `results.json`, `actor_net.pth`, `critic_net.pth`, `mixer_net.pth` 저장

짧은 smoke run이므로 성능 수치는 논문 결과 재현값으로 해석하면 안 된다. 전체 논문 수준 평가를 하려면 README에 적힌 PRIMAL test map 자료를 별도로 받아 `instances/primal_test_envs`에 배치해야 한다.

## 2. 생성한 실행 소스코드

추가한 파일:

- `run_cactus_smoke.py`: 원본 `rl4mapf` 패키지를 import해 작은 CACTUS 실행을 수행하는 스크립트
- `requirements-cactus-smoke.txt`: 최소 실행 의존성
- `recommended_patch_policy_parameters.diff`: 실행 중 발견한 gradient clipping 경고에 대한 권장 패치

재실행 명령:

```powershell
& 'C:\my-project\2. smartfactory\5\5\.venv\Scripts\python.exe' 'C:\my-project\2. smartfactory\5\5\run_cactus_smoke.py'
```

설치된 최소 의존성:

- Python 3.12.13
- torch 2.11.0+cpu
- numpy 2.4.4
- pygame 2.6.1

## 3. 실행 결과

성공 실행 경로:

`C:\my-project\2. smartfactory\5\5\cactus_smoke_output\quick-run-20260505-162050`

생성 파일:

- `results.json`
- `run_summary.json`
- `actor_net.pth`
- `critic_net.pth`
- `mixer_net.pth`

주요 실행 설정:

- 알고리즘: `PPO_QMIX`
- curriculum: `CACTUS`
- agent 수: 2
- map size: 6
- epoch: 2
- episodes per epoch: 1
- time limit: 12
- render: false

최종 smoke 결과:

```json
{
  "success_rate": [0.0, 0.0, 0.0],
  "completion_rate": [0.0, 0.0, 0.0],
  "total_time": 0.38538050651550293
}
```

짧은 무작위 초기 학습 run이라 성공률이 0인 것은 자연스럽다. 중요한 점은 원본 코드의 학습 경로가 실행되고 결과와 모델 가중치가 저장됐다는 것이다.

## 4. 코드 구조 분석

### 4.1 실험 진입점

`run_training.py`는 기본 파라미터를 만든 뒤 다음 7개 실험을 순차 실행한다.

- `PPO_QMIX + CACTUS`
- `PPO_QMIX + Random`
- `PPO_QPLEX + CACTUS`
- `PPO_QPLEX + Random`
- `MAPPO + CACTUS`
- `MAPPO + Random`
- `PRIMAL + Random`

각 실험은 `maps.generate_training_maps(params)`로 16개 training map을 만들고, `algorithms.make(params)`로 controller를 만든 뒤 `experiments.run_training(...)`에 넘긴다.

### 4.2 CACTUS curriculum 구현

핵심 구현은 `cactus/curriculum.py`의 `CACTUSCurriculum`이다.

- 초기 radius는 `2`
- 각 환경에 `env.set_init_goal_radius(self.radius)`를 적용
- 매 epoch마다 completion rate를 sliding window에 누적
- 평균과 표준편차를 계산
- `mean - deviation_factor * stddev >= improvement_threshold`이면 radius를 1 증가
- 증가한 radius를 모든 환경에 다시 적용

논문 설명과 코드가 대응된다. 논문은 평균 completion rate `mu`가 threshold `U`를 신뢰수준 조건 `mu - eta*sigma >= U`로 넘으면 allocation radius를 증가시키는 구조를 설명한다.

주의할 점은 코드의 `adjust_threshold()`가 비어 있다는 점이다. 즉 threshold를 동적으로 조정하는 확장은 들어 있지 않고, 기본 threshold는 고정값이다.

### 4.3 환경과 goal radius

`cactus/env/gridworld.py`의 `reset()`은 agent 시작 위치를 무작위로 뽑고, `init_goal_radius`가 설정되어 있으면 시작점 주변 radius 안에서 goal 후보를 뽑는다. 이것이 논문에서 말하는 reverse curriculum의 실제 작동 지점이다.

또 하나의 구현상 특징은 `cactus/env/env_generator.py`의 obstacle 생성이다. `density=0`이어도 `max(4, int(size*size*density) + 1)` 때문에 작은 smoke map에서도 장애물이 일부 생길 수 있다. 따라서 `density=0`을 완전한 무장애 맵으로 해석하면 안 된다.

### 4.4 학습 루프

`cactus/experiments.py`의 흐름은 단순하다.

1. `curr.make(params)(envs, params)`로 curriculum 생성
2. 매 epoch 시작 시 직전 training result로 `curriculum.update_curriculum(...)`
3. `run_episodes(...)`로 training episode 실행
4. log interval마다 `test_run(...)`으로 평가
5. 2000 epoch마다, 그리고 마지막에 결과 JSON과 모델 가중치 저장

이번 smoke run에서는 `DIRECTORY`를 지정했기 때문에 마지막 저장 단계까지 확인했다.

### 4.5 Controller와 네트워크

`cactus/algorithms.py`는 algorithm name에 따라 controller와 critic 구성을 바꾼다.

- `PPO_QMIX`: PPO controller + QMIX critic
- `PPO_QPLEX`: PPO controller + QPLEX critic
- `MAPPO`: PPO controller + Central critic
- `PRIMAL`: PRIMAL controller

Actor는 `cactus/modules/ffn_module.py`의 단순 feed-forward network다. Q 계열 critic은 `cactus/modules/q_module.py`에 있으며, QMIX mixer와 QPLEX mixer도 같은 파일에 구현되어 있다.

## 5. 실행 중 발견한 이슈

### 5.1 gradient clipping 경고

실행 중 다음 경고가 발생했다.

```text
UserWarning: `parameters` is an empty generator, no gradient clipping will occur.
```

원인은 `cactus/controller/a2c_controller.py`에서 `self.policy_parameters = self.policy_network.parameters()`로 generator를 저장하고, 이를 optimizer 생성에 사용한 뒤 나중에 gradient clipping에도 재사용하기 때문이다. optimizer 생성 과정에서 generator가 소비되어 clipping 시점에는 비어 있을 수 있다.

권장 수정은 generator를 list로 보관하는 것이다.

```python
self.policy_parameters = list(self.policy_network.parameters())
self.policy_optimizer = torch.optim.Adam(self.policy_parameters, lr=self.learning_rate)
```

동일한 이유로 non-shared critic의 `self.critic_parameters`도 list로 두는 편이 안전하다. 패치 초안은 `recommended_patch_policy_parameters.diff`에 저장했다.

### 5.2 README 기준 평가 데이터는 별도 필요

`eval.py`는 `instances/primal_test_envs/*.npy` 파일을 요구한다. 이 자료는 저장소에 포함되어 있지 않고 PRIMAL GitHub 저장소가 참조하는 Google Drive 자료를 받아야 한다. 따라서 저장소 clone만으로는 논문 평가표 전체를 즉시 재현할 수 없다.

### 5.3 원본 full training은 장시간 실행용

`run_training.py` 기본값은 `NUMBER_OF_EPOCHS=5000`, `EPISODES_PER_EPOCH=32`이고 여러 알고리즘을 연속 실행한다. 논문은 CPU 기반 실험이라고 설명하지만, 노트북/일반 작업 환경에서 즉시 돌릴 수 있는 규모는 아니다.

## 6. 논문과 코드의 대응 요약

논문 아이디어는 코드에 비교적 직접적으로 반영되어 있다.

- allocation radius: `CACTUSCurriculum.radius`
- radius 초기 적용: `env.set_init_goal_radius(self.radius)`
- confidence update: `mean - deviation_factor * stddev >= improvement_threshold`
- goal sampling by radius: `GridWorld.reset()`
- completion rate metric: `GridWorld.step()`의 `ENV_COMPLETION_RATE`
- training/evaluation orchestration: `experiments.run_training()`

CACTUS 자체는 크고 복잡한 새 네트워크라기보다, 기존 MARL controller의 training distribution을 조정하는 curriculum layer에 가깝다. 이 때문에 구현상 핵심 파일은 `curriculum.py`, `gridworld.py`, `experiments.py` 세 곳이다.

## 7. 다음 단계 제안

1. `recommended_patch_policy_parameters.diff`를 실제 코드에 적용한 뒤 warning이 사라지는지 재실행한다.
2. PRIMAL test map을 받아 `eval.py` 기준 평가 경로를 검증한다.
3. `PPO_QMIX + CACTUS`와 `PPO_QMIX + Random`을 같은 작은 설정으로 비교해 curriculum radius 변화와 completion curve를 별도 JSON/그래프로 저장한다.

