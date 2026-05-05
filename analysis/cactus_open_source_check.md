# Confidence-Based Curriculum Learning for MAPF 오픈소스 확인

확인일: 2026-05-05

## 결론

`Confidence-Based Curriculum Learning for Multi-Agent Path Finding` 및 확장 논문
`Confidence-Based Curricula for Multi-Agent Path Finding via Reinforcement Learning`은
공개 GitHub 저장소를 제공한다.

- 논문 저자 페이지: https://thomyphan.github.io/publication/2024-05-01-aamas-phan
- 코드 저장소: https://github.com/thomyphan/rl4mapf
- Springer 확장 논문 Code availability: https://link.springer.com/article/10.1007/s10458-026-09747-7

## 구현 및 분석 가능성

가능하다. 저장소는 public이며 Python 코드로 구성되어 있고, README 기준으로
CACTUS 알고리즘, 학습 스크립트(`run_training.py`), 평가 스크립트(`eval.py`),
예시 모델(`example_models`)을 포함한다.

주의할 점:

- GitHub 릴리스는 별도로 없다.
- README에는 별도 `requirements.txt`가 보이지 않아 의존성은 코드에서 역추적해야 한다.
- 테스트 맵은 PRIMAL GitHub 저장소가 참조하는 Google Drive 자료를 별도로 받아야 한다.
- 라이선스 파일은 공개 사용을 허용하지만 상업적 사용은 USC Stevens Center for Innovation에
  문의하라는 문구가 있어, 연구/교육 목적 분석에는 적합하나 상업적 재사용은 확인이 필요하다.

