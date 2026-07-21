#!/usr/bin/env python3
"""
Run Self-Proposing Exploration with PolySkill

This script enables agents to:
1. Autonomously explore websites
2. Propose their own goals/tasks
3. Learn polymorphic skills from successful attempts
4. Build a library of transferable skills without predefined tasks

This represents the "task-free" continual learning setting from the paper.
"""

import argparse
import yaml

from polyskill.exploration.explore_loop import run_self_proposing_exploration


def main():
    parser = argparse.ArgumentParser(
        description="Run self-proposing exploration with PolySkill"
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML config file"
    )
    parser.add_argument(
        "--domain",
        type=str,
        choices=["shopping", "dev_tools", "mixed"],
        default="mixed",
        help="Domain(s) for exploration"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=150,
        help="Number of exploration iterations"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4.1",
        help="Model config key to use (must match a key in model_configs)"
    )

    args = parser.parse_args()

    # Load config
    with open(args.config, "r") as f:
        config_dict = yaml.safe_load(f)

    skill_induction = config_dict.get("skill_induction", {})
    exploration = config_dict.get("exploration", {})
    model_configs = config_dict.get("model_configs", {})

    # Resolve model config: CLI --model selects the key; fall back to first entry
    if args.model in model_configs:
        model_config = model_configs[args.model]
    elif model_configs:
        model_config = next(iter(model_configs.values()))
    else:
        model_config = None

    storage_path = skill_induction.get("storage_path", "./results/self_proposing_skills/")
    websites = exploration.get("websites", None)
    domain = args.domain if args.domain != "mixed" else exploration.get("domain", "shopping")
    iterations = args.iterations

    print(f"""
Self-Proposing Exploration — PolySkill
  Domain:     {domain}
  Iterations: {iterations}
  Model:      {args.model}
  Config:     {args.config}
  Storage:    {storage_path}
    """)

    stats = run_self_proposing_exploration(
        domain=domain,
        iterations=iterations,
        model_config=model_config,
        storage_path=storage_path,
        websites=websites,
    )

    print("\n" + "="*60)
    print("SELF-PROPOSING EXPLORATION COMPLETE")
    print("="*60)
    print(f"Iterations run:  {stats['iterations']}")
    print(f"Successes:       {stats['successes']}")
    print(f"Coverage:        {stats['coverage']}")
    skill_info = stats.get("skills", {})
    if isinstance(skill_info, dict):
        print(f"Skills induced:  {skill_info.get('total_skills', 0)}")
    print("="*60)

    return stats


if __name__ == "__main__":
    main()
