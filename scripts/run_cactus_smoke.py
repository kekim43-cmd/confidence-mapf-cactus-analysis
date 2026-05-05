"""Small reproducibility run for thomyphan/rl4mapf CACTUS code.

This script imports the upstream repository without modifying it and runs a
tiny PPO_QMIX + CACTUS training loop on generated MAPF maps. It is intended as
a smoke test, not as a reproduction of the full paper experiments.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any


os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent if script_dir.name == "scripts" else script_dir
    parser = argparse.ArgumentParser(description="Run a small CACTUS smoke test.")
    parser.add_argument("--repo", type=Path, default=root / "rl4mapf")
    parser.add_argument("--output", type=Path, default=root / "cactus_smoke_output")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--agents", type=int, default=2)
    parser.add_argument("--map-size", type=int, default=6)
    parser.add_argument("--density", type=float, default=0.0)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--episodes-per-epoch", type=int, default=1)
    parser.add_argument("--time-limit", type=int, default=12)
    parser.add_argument("--hidden-dim", type=int, default=16)
    return parser.parse_args()


def make_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): make_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [make_jsonable(item) for item in value]
    if hasattr(value, "tolist"):
        return make_jsonable(value.tolist())
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            return str(value)
    return str(value)


def main() -> int:
    args = parse_args()
    repo = args.repo.resolve()
    if not repo.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo}")

    sys.path.insert(0, str(repo))

    import numpy
    import torch

    import cactus.algorithms as algorithms
    import cactus.env.env_generator as env_generator
    import cactus.experiments as experiments
    from cactus.constants import (
        ALGORITHM_NAME,
        ALGORITHM_PPO_QMIX,
        CACTUS_CURRICULUM,
        CURRICULUM_NAME,
        DEVIATION_FACTOR,
        DIRECTORY,
        ENV_GAMMA,
        ENV_MAKESPAN_MODE,
        ENV_NR_AGENTS,
        ENV_OBSERVATION_SIZE,
        ENV_TIME_LIMIT,
        EPISODES_PER_EPOCH,
        EPOCH_LOG_INTERVAL,
        GRAD_NORM_CLIP,
        HIDDEN_LAYER_DIM,
        IMPROVEMENT_THRESHOLD,
        MIXING_HIDDEN_SIZE,
        NUMBER_OF_EPOCHS,
        RADIUS_UPDATE_INTERVAL,
        RENDER_MODE,
        REWARD_SHARING,
        SAMPLE_NR_AGENTS,
        SLIDING_WINDOW_SIZE,
        TEST_INIT_GOAL_RADIUS,
        VDN_MODE,
    )

    random.seed(args.seed)
    numpy.random.seed(args.seed)
    torch.manual_seed(args.seed)

    run_id = time.strftime("quick-run-%Y%m%d-%H%M%S")
    run_dir = (args.output / run_id).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    params = {
        ENV_OBSERVATION_SIZE: 5,
        ENV_NR_AGENTS: args.agents,
        SAMPLE_NR_AGENTS: args.agents,
        HIDDEN_LAYER_DIM: args.hidden_dim,
        NUMBER_OF_EPOCHS: args.epochs,
        EPISODES_PER_EPOCH: args.episodes_per_epoch,
        EPOCH_LOG_INTERVAL: 1,
        RADIUS_UPDATE_INTERVAL: 1,
        ENV_TIME_LIMIT: args.time_limit,
        TEST_INIT_GOAL_RADIUS: None,
        ENV_GAMMA: 1,
        RENDER_MODE: False,
        ENV_MAKESPAN_MODE: False,
        GRAD_NORM_CLIP: 10,
        VDN_MODE: False,
        REWARD_SHARING: False,
        MIXING_HIDDEN_SIZE: args.hidden_dim,
        ALGORITHM_NAME: ALGORITHM_PPO_QMIX,
        CURRICULUM_NAME: CACTUS_CURRICULUM,
        DIRECTORY: str(run_dir),
        SLIDING_WINDOW_SIZE: 2,
        IMPROVEMENT_THRESHOLD: 0.75,
        DEVIATION_FACTOR: 2,
    }

    env, _ = env_generator.generate_mapf_gridworld(
        args.agents,
        args.map_size,
        args.density,
        params,
    )
    envs = [env]
    test_envs = [copy.deepcopy(env)]
    controller = algorithms.make(params)

    started = time.time()
    result = experiments.run_training(envs, test_envs, controller, params)
    elapsed = time.time() - started

    summary = {
        "purpose": "Minimal smoke test for upstream CACTUS/MAPF implementation",
        "repo": str(repo),
        "run_dir": str(run_dir),
        "seed": args.seed,
        "elapsed_seconds": elapsed,
        "parameters": params,
        "result": result,
        "environment": {
            "python": sys.version,
            "torch": torch.__version__,
            "numpy": numpy.__version__,
        },
    }

    summary_path = run_dir / "run_summary.json"
    summary_path.write_text(json.dumps(make_jsonable(summary), indent=2), encoding="utf-8")
    print(json.dumps(make_jsonable(summary), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
