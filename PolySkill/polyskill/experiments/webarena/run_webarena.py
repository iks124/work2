#!/usr/bin/env python3
"""
Run WebArena experiments with PolySkill

This script runs evaluations on the WebArena benchmark with polymorphic skill induction.
WebArena includes realistic websites across multiple categories:
- Shopping (OneStopShop)
- Admin (CMS)
- Reddit (Forum)
- GitLab (Development)
- Map (OpenStreetMap)
- Cross-website tasks
"""

import argparse

from polyskill.experiments.run_eval_with_skill_induction import SkillInductionEvaluator


def main():
    parser = argparse.ArgumentParser(description="Run WebArena experiments with PolySkill")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML config file"
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=["shopping", "admin", "reddit", "gitlab", "map", "cross", "all"],
        default="all",
        help="WebArena category to evaluate"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4.1",
        help="Model to use (gpt-4.1, claude-3-7-sonnet-20250219, qwen3-coder-480b-a35b, glm-4.5)"
    )

    args = parser.parse_args()

    print(f"""
WebArena Evaluation — PolySkill
  Category: {args.category}
  Model:    {args.model}
  Config:   {args.config}
    """)

    # Run evaluation, threading --category into benchmark configs
    evaluator = SkillInductionEvaluator(args.config, category=args.category, model=args.model)
    evaluator.run_evaluation()

    # Print skills summary
    evaluator.print_skills_summary()


if __name__ == "__main__":
    main()
