#!/usr/bin/env python3
"""
Run Mind2Web experiments with PolySkill

This script runs evaluations on the Mind2Web benchmark with polymorphic skill induction.
Supports three evaluation settings:
- Cross-task: Generalization to new tasks on seen websites
- Cross-website: Generalization to new websites in seen domains
- Cross-domain: Generalization to entirely new domains
"""

import argparse

from polyskill.experiments.run_eval_with_skill_induction import SkillInductionEvaluator


def main():
    parser = argparse.ArgumentParser(description="Run Mind2Web experiments with PolySkill")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML config file"
    )
    parser.add_argument(
        "--setting",
        type=str,
        choices=["cross-task", "cross-website", "cross-domain", "all"],
        default="cross-task",
        help="Evaluation setting"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4.1",
        help="Model to use (gpt-4.1, claude-3-7-sonnet-20250219, qwen3-coder-480b-a35b, glm-4.5)"
    )

    args = parser.parse_args()

    print(f"""
Mind2Web Evaluation — PolySkill
  Setting: {args.setting}
  Model:   {args.model}
  Config:  {args.config}
    """)

    # Run evaluation, threading --setting into benchmark configs
    evaluator = SkillInductionEvaluator(args.config, setting=args.setting, model=args.model)
    evaluator.run_evaluation()

    # Print skills summary
    evaluator.print_skills_summary()


if __name__ == "__main__":
    main()
