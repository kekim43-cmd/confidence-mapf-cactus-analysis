# Confidence-Based Curriculum Learning for MAPF 코드 실행 및 분석

이 저장소는 논문 **Confidence-Based Curriculum Learning for Multi-Agent Path Finding**의 공개 구현체를 로컬에서 실행해 보고, 핵심 구조를 정리한 분석 자료입니다.

대상 공개 저장소:

- https://github.com/thomyphan/rl4mapf

## 포함 내용

- `analysis/cactus_source_analysis_report.md`: 코드 실행 및 구현 분석 보고서
- `analysis/cactus_open_source_check.md`: 오픈소스 공개 여부 확인 메모
- `scripts/run_cactus_smoke.py`: 원본 `rl4mapf`를 수정하지 않고 최소 학습 루프를 돌리는 smoke test 스크립트
- `results/quick-run-20260505-162050`: 실제 실행 결과 요약 JSON
- `patches/recommended_patch_policy_parameters.diff`: 실행 중 발견한 gradient clipping 경고에 대한 권장 패치

## 재실행 방법

```powershell
git clone https://github.com/thomyphan/rl4mapf.git rl4mapf
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\scripts\run_cactus_smoke.py
```

이번 검증은 논문 전체 재현이 아니라 end-to-end smoke test입니다. 원본 `run_training.py`는 5000 epoch와 여러 알고리즘 조합을 연속 실행하므로 장시간이 필요합니다. 논문 평가를 그대로 재현하려면 PRIMAL test map 자료를 별도로 받아 `instances/primal_test_envs`에 배치해야 합니다.

## 실행 환경

- Python 3.12.13
- torch 2.11.0+cpu
- numpy 2.4.4
- pygame 2.6.1

