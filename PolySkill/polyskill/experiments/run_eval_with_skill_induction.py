#!/usr/bin/env python3
"""
Run Evaluation with Online Skill Induction

This script runs evaluations in single-threaded mode where each task can benefit
from skills learned from previous successful tasks.

Flow:
1. Run task n
2. Judge if successful using webjudge_general
3. If successful, induce skills
4. Skills are available for task n+1

Key: threads=1 to ensure sequential execution.
"""

import yaml
import fire
import logging

from polyskill.evaluation.eval_config import EvalConfig
from polyskill.skill_induction.judge.utils import load_trajectory_data, extract_task_from_trajectory

logger = logging.getLogger(__name__)


class SkillInductionEvaluator:
    """
    Handles evaluation with online skill induction.
    """

    def __init__(self, config_path: str, category: str = None, setting: str = None,
                 model: str = None):
        # Load config
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f.read())

        # Extract skill induction config
        self.skill_config = config_dict.pop("skill_induction", {})
        # Remove exploration keys so EvalConfig (extra="ignore") doesn't choke
        config_dict.pop("exploration", None)
        config_dict.pop("exploration_domains", None)

        # Thread --category / --setting overrides into benchmark dicts before
        # constructing EvalConfig so the validated object already has the right values.
        if category and category != "all":
            for bname, bcfg in config_dict.get("benchmarks", {}).items():
                if isinstance(bcfg, dict) and bcfg.get("dataset") == "webarena":
                    bcfg["category"] = category

        if setting and setting != "all":
            for bname, bcfg in config_dict.get("benchmarks", {}).items():
                if isinstance(bcfg, dict) and bcfg.get("dataset") == "mind2web":
                    bcfg["setting"] = setting

        # Thread the --model override: match a model_configs entry by key or by its
        # configured model name, then point every agent at that entry.
        if model:
            model_configs = config_dict.get("model_configs", {}) or {}
            match = None
            for key, mcfg in model_configs.items():
                if key == model or (isinstance(mcfg, dict) and mcfg.get("name") == model):
                    match = key
                    break
            if match is None:
                available = sorted(
                    set(model_configs)
                    | {m.get("name") for m in model_configs.values()
                       if isinstance(m, dict) and m.get("name")}
                )
                raise ValueError(
                    f"--model {model!r} does not match any model_configs entry in "
                    f"{config_path}. Available: {available}"
                )
            for aname, acfg in config_dict.get("agents", {}).items():
                if isinstance(acfg, dict):
                    acfg["model_config_name"] = match
            print(f"Model override: agents -> model_configs[{match!r}]")

        # Create eval config
        self.eval_config = EvalConfig(**config_dict)

        # Force single-threaded execution
        if self.eval_config.runner.threads != 1:
            print(f"WARNING: Forcing threads=1 for skill induction (was {self.eval_config.runner.threads})")
            self.eval_config.runner.threads = 1

        # Inject skill config into all agents (so eval_loop.py hook can access it)
        if self.skill_config.get("enabled", True):
            for agent_name, agent_config in self.eval_config.agents.items():
                agent_config.skill_induction_config = self.skill_config
                print(f"Injected skill induction config into agent: {agent_name}")

        # Track evaluation state for summary
        self.task_count = 0
        self.successful_tasks = 0
        self.induced_skills = 0

    @staticmethod
    def _task_dir_name(env_id: str, task_kwargs, index: int) -> str:
        """Directory name for one task's trajectory (must be unique per task).

        For miniwob/webarena the env id already identifies the task, so use it
        (with '/' and '.' made dir-safe). For Mind2Web every task shares the
        ``browsergym/openended`` env id, so key off ``task_id`` (prefixed with a
        running index) to avoid collisions.
        """
        import re

        task_id = (task_kwargs or {}).get("task_id")
        if task_id:
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(task_id))
            return f"{index:04d}_{safe}"
        return env_id.replace("/", "_")

    def _run_and_induce(
        self,
        env_id: str,
        task_kwargs,
        agent_config,
        benchmark_config,
        output_dir: str,
        judge_method: str,
        score_threshold: int,
        index: int = 0,
    ):
        """Run ONE task into its own per-task directory, then judge + induce.

        Returns ``(reward, skill_or_None, judged)`` where ``judged`` is the LLM
        WebJudge verdict. For live ``openended`` tasks (Mind2Web) the gold reward
        is always 0.0, so ``judged`` -- not ``reward`` -- is the success signal
        the paper reports.

        The trajectory is read back as a DIRECTORY: ``eval_loop.run_example``
        writes ``summary_info.json`` + ``step_*.pkl.gz`` directly into its
        ``debug_dirs[0]`` (no ``env_id`` subdir, no ``.pb.xz`` protobuf), and
        ``process_task_for_skills_sync`` -> ``load_trajectory_data`` ->
        ``load_trajectory`` reads those step files from that directory. Each task
        gets a unique directory so tasks don't overwrite each other's steps.
        """
        import os
        from polyskill.evaluation.eval_loop import run_example
        from polyskill.skill_induction.online_hook import (
            judge_trajectory_success_sync,
            process_task_for_skills_sync,
        )

        # Per-task directory (env ids contain '/' and '.', neither dir-safe; and
        # Mind2Web reuses one env id for every task, so fall back to task_id).
        task_dir = os.path.join(output_dir, self._task_dir_name(env_id, task_kwargs, index))

        reward = run_example(
            env_id,
            task_kwargs,
            agent_config,
            benchmark_config,
            debug_dirs=[task_dir],
            timeout=self.eval_config.runner.timeout_secs,
            seed=self.eval_config.runner.seed,
        )

        skill = None
        judged = False
        if self.skill_config.get("enabled", True):
            summary_path = os.path.join(task_dir, "summary_info.json")
            if os.path.exists(summary_path):
                # A BrowserGym setup/navigation failure still writes a summary, but
                # produces no step files.  Do not ask an LLM to judge that empty
                # trajectory: some models can interpret the empty prompt as success,
                # which would inflate the reported Mind2Web success rate.
                import glob
                if not glob.glob(os.path.join(task_dir, "step_*.pkl.gz")):
                    print("  - Empty trajectory (browser setup failed); counting as judged failure")
                    return reward, None, False

                # Prefer the task's own goal text: the kwarg goal (Mind2Web) first,
                # then the goal recorded in the trajectory, then the env id.
                task_goal = (task_kwargs or {}).get("goal")
                if not task_goal:
                    task_goal = env_id
                    try:
                        from polyskill.skill_induction.judge.utils import (
                            load_trajectory_data,
                            extract_task_from_trajectory,
                        )

                        traj = load_trajectory_data(task_dir)
                        goal = extract_task_from_trajectory(traj)
                        if goal:
                            task_goal = goal
                    except Exception as e:  # noqa: BLE001 - goal extraction is best-effort
                        logger.debug("Could not extract goal from %s: %s", task_dir, e)

                print(
                    f"  Judging with LLM (method: {judge_method}, "
                    f"score_threshold: {score_threshold})..."
                )

                # Judge once for the (judge-based) success signal, then reuse that
                # verdict for induction so the LLM judge is not called twice.
                use_reward_signal = self.skill_config.get("use_reward_signal", False)
                if use_reward_signal and reward <= 0:
                    judged = False
                else:
                    judge_config = self.skill_config.get("judge_model", {
                        "provider": "openai", "name": "gpt-4o", "temperature": 0.0,
                    })
                    judged = judge_trajectory_success_sync(
                        trajectory_path=task_dir,
                        judge_config=judge_config,
                        judge_method=judge_method,
                        score_threshold=score_threshold,
                    )

                # trajectory_path MUST be the directory (load_trajectory reads
                # step_*.pkl.gz from it).
                per_task_skill_config = self.skill_config.copy()
                if task_kwargs:
                    if task_kwargs.get("domain"):
                        per_task_skill_config["domain"] = task_kwargs["domain"]
                    if task_kwargs.get("website"):
                        per_task_skill_config["site"] = task_kwargs["website"]

                skill = process_task_for_skills_sync(
                    trajectory_path=task_dir,
                    task=task_goal,
                    reward=reward,
                    agent_config=agent_config,
                    skill_config=per_task_skill_config,
                    judged=judged,
                )
            else:
                print(f"  - No trajectory found at {task_dir} for LLM judging")

        return reward, skill, judged

    def print_skills_summary(self):
        """Print summary of learned skills."""
        try:
            from polyskill.skill_induction.online_hook import get_skills_summary
            storage_path = self.skill_config.get("storage_path", "./learned_skills/")
            summary = get_skills_summary(storage_path)

            print(f"\n{'='*60}")
            print("LEARNED SKILLS SUMMARY")
            print(f"{'='*60}")
            print(summary)
        except Exception as e:
            logger.warning(f"Failed to get skills summary: {e}")

    def run_evaluation(self):
        """Run evaluation with true online skill induction."""
        print("="*60)
        print("RUNNING EVALUATION WITH ONLINE SKILL INDUCTION")
        print("="*60)
        print(f"Single-threaded execution: {self.eval_config.runner.threads == 1}")
        print(f"Skill induction enabled: {self.skill_config.get('enabled', True)}")
        judge_method = self.skill_config.get('judge_method', 'webjudge_general')
        print(f"Judge method: {judge_method}")
        print(f"Use reward signal: {self.skill_config.get('use_reward_signal', False)}")

        # Always resolve score_threshold before any branch that might read it.
        score_threshold = self.skill_config.get('score_threshold', 3)

        # Special handling for Mind2Web configuration
        if judge_method == 'webjudge_online_mind2web':
            print(f"Using WebJudge Online Mind2Web evaluation")
            print(f"Screenshot score threshold: {score_threshold} (1-5 scale)")
            print(f"Mind2Web-specific criteria: filters, sorting, range requirements")
            if self.eval_config.runner.threads != 1:
                print("WARNING: Mind2Web skill induction requires threads=1 for sequential learning")

        if self.skill_config.get("enabled", True):
            print("Skills will be induced after each successful task")
            print("Each task can benefit from previously learned skills")

        # Import required functions for task-by-task execution.
        # (run_example / process_task_for_skills_sync are imported inside
        # _run_and_induce, which owns the per-task run+judge+induce block.)
        import os
        import subprocess
        from tqdm import tqdm
        from polyskill.evaluation.eval_runner import get_env_ids_and_task_kwargs, wait_for_models, _get_output_dirs_for_run

        # Run each benchmark-agent combination
        all_results = []
        for benchmark_name, benchmark_config in self.eval_config.benchmarks.items():
            for agent_name, agent_config in self.eval_config.agents.items():
                print(f"\n{'='*40}")
                print(f"RUNNING: {benchmark_name} with {agent_name}")
                print(f"{'='*40}")

                # Resolve model config like the regular evaluation system
                if not agent_config.model_config_name:
                    raise ValueError(f"No model_config_name in agent {agent_name}. There should be exactly one model_config_name in agent.")
                if agent_config.model_config_name not in self.eval_config.model_configs:
                    raise ValueError(f"Model config {agent_config.model_config_name} not found in model_configs.")

                # Set the resolved model config
                agent_config.model = self.eval_config.model_configs[agent_config.model_config_name]

                # Get environment IDs and task kwargs for this benchmark
                env_ids, task_kwargs = get_env_ids_and_task_kwargs(
                    benchmark_config, shuffle_seed=self.eval_config.runner.seed
                )
                if task_kwargs:
                    assert len(env_ids) == len(task_kwargs), f"Expect arguments for every environment ID, found {len(env_ids)} envs and {len(task_kwargs)} args."

                # Wait for models to be ready
                wait_for_models(agent_config.model)

                # Create output directories following run_single_benchmark pattern
                output_dirs = _get_output_dirs_for_run(
                    self.eval_config,
                    benchmark_name=benchmark_name,
                    agent_name=agent_name
                )

                # Print output directory information
                if output_dirs:
                    print(f"Results will be saved to: {output_dirs[0]}")

                # Reset WebArena environment if needed
                if benchmark_config.reset_env and "webarena" in benchmark_config.dataset:
                    import os as _os
                    reset_script = "scripts/reset_remote_wa_vwa.sh"
                    if _os.path.exists(reset_script):
                        print("Resetting WebArena environment...")
                        try:
                            subprocess.run(["bash", reset_script], check=False)
                        except Exception as e:
                            print(f"Warning: Failed to reset WebArena environment: {e}")
                    else:
                        print(
                            "Note: no reset script found; WebArena env reset is the "
                            "operator's responsibility (see docs/WEBARENA.md). Continuing."
                        )

                print(f"Found {len(env_ids)} tasks to run sequentially")
                if self.skill_config.get("enabled", True):
                    storage_path = self.skill_config.get("storage_path", "./learned_skills/")
                    print(f"Skills will be stored at: {storage_path}")

                # Run tasks one by one with immediate skill induction
                task_rewards = []
                skills_learned = 0
                judged_successes = 0
                judge_ran = self.skill_config.get("enabled", True)
                empty_trajectories = 0
                runtime_failures = 0
                wall_clock_timeouts = 0

                # Use progress bar like run_single_benchmark
                with tqdm(total=len(env_ids), desc=f"{benchmark_name}+{agent_name}") as pbar:
                    for i, env_id in enumerate(env_ids):
                        print(f"\n[Task {i+1}/{len(env_ids)}] {env_id}")

                        # Inject current skills into agent config before task
                        if self.skill_config.get("enabled", True):
                            try:
                                from polyskill.skill_induction.online_hook import get_current_skills, get_skills_summary

                                # Get current skills and inject them into agent config
                                current_skills = get_current_skills(storage_path)
                                skill_count = len(current_skills)

                                # Update agent config with current skills for this task
                                agent_config.skill_induction_config = self.skill_config.copy()
                                agent_config.skill_induction_config['current_skills'] = current_skills
                                agent_config.skill_induction_config['storage_path'] = storage_path

                                print(f"  Available skills injected into agent: {skill_count}")
                                if skill_count > 0:
                                    summary = get_skills_summary(storage_path)
                                    # Show first few lines of skills for context
                                    summary_lines = summary.split('\n')[:3]
                                    print(f"  Recent skills: {' | '.join(line.strip() for line in summary_lines if line.strip())}")
                            except Exception as e:
                                print(f"  Available skills: 0 (error: {e})")

                        # Run single task into its own per-task dir, then judge +
                        # induce. _run_and_induce reads the trajectory back as a
                        # DIRECTORY (step_*.pkl.gz + summary_info.json), so each
                        # task no longer overwrites the previous task's steps and
                        # induction actually fires.
                        try:
                            reward, skill, judged = self._run_and_induce(
                                env_id=env_id,
                                task_kwargs=None if not task_kwargs else task_kwargs[i],
                                agent_config=agent_config,
                                benchmark_config=benchmark_config,
                                output_dir=output_dirs[0] if output_dirs else "./results",
                                judge_method=judge_method,
                                score_threshold=score_threshold,
                                index=i,
                            )
                        except Exception as e:
                            print(f"  Task run/induction failed: {e}")
                            reward, skill, judged = 0.0, None, False

                        task_rewards.append(reward)

                        # Keep infrastructure/runtime failures separate from
                        # ordinary agent or judge failures in the final report.
                        import glob
                        import json
                        task_dir = os.path.join(
                            output_dirs[0] if output_dirs else "./results",
                            self._task_dir_name(
                                env_id,
                                None if not task_kwargs else task_kwargs[i],
                                i,
                            ),
                        )
                        if not glob.glob(os.path.join(task_dir, "step_*.pkl.gz")):
                            empty_trajectories += 1
                        try:
                            with open(os.path.join(task_dir, "summary_info.json"), "r") as f:
                                task_summary = json.load(f)
                            task_error = str(task_summary.get("error") or "")
                            if task_error:
                                runtime_failures += 1
                            if "Wall-clock timeout" in task_error:
                                wall_clock_timeouts += 1
                        except (OSError, ValueError):
                            pass
                        if judged:
                            judged_successes += 1
                        golden_reward_success = reward > 0
                        print(f"  Golden reward: {'SUCCESS' if golden_reward_success else 'FAILED'} (reward: {reward})")

                        if skill:
                            skills_learned += 1
                            print(f"  LLM Judge: SUCCESS - Learned skill: {skill.name}")
                            if judge_method == 'webjudge_online_mind2web':
                                print(f"    Mind2Web evaluation passed with score threshold {score_threshold}")
                            # Update agent with new skills immediately
                            try:
                                from polyskill.skill_induction.online_hook import get_current_skills
                                updated_skills = get_current_skills(storage_path)
                                print(f"  Skills now available for next task: {len(updated_skills)}")
                            except Exception as e:
                                print(f"  - Warning: Could not update skills for agent: {e}")
                        elif self.skill_config.get("enabled", True):
                            if judge_method == 'webjudge_online_mind2web':
                                print("  - LLM Judge: FAILED - Task did not meet Mind2Web evaluation criteria")
                            else:
                                print("  - LLM Judge: FAILED or no skill pattern found")

                        # Update progress bar
                        pbar.update(1)

                # Calculate results following run_single_benchmark format.
                # gold_success = environment reward; judged_success = LLM WebJudge.
                num_success = sum(task_rewards)
                num_total = len(task_rewards)
                gold_success_rate = num_success / num_total if num_total > 0 else 0
                judged_success_rate = judged_successes / num_total if num_total > 0 else 0

                # Mind2Web openended tasks have no gold reward, so the judge-based
                # SR is the headline metric (matching the paper). WebArena keeps the
                # gold reward as headline but still reports the judged SR when the
                # judge ran.
                is_mind2web = getattr(benchmark_config, "dataset", None) == "mind2web"
                if is_mind2web:
                    success_rate = judged_success_rate
                    print(f"\nSuccess rate (judged): {judged_success_rate:.1%} "
                          f"({judged_successes}/{num_total})")
                    print(f"Success rate (gold reward): {gold_success_rate:.1%} "
                          f"({num_success}/{num_total})")
                else:
                    success_rate = gold_success_rate
                    print(f"\nSuccess rate (gold reward): {gold_success_rate:.1%} "
                          f"({num_success}/{num_total})")
                    if judge_ran:
                        print(f"Success rate (judged): {judged_success_rate:.1%} "
                              f"({judged_successes}/{num_total})")
                print(f"Skills learned: {skills_learned}")
                print(
                    "Failure breakdown: "
                    f"empty trajectories={empty_trajectories}, "
                    f"runtime failures={runtime_failures}, "
                    f"wall-clock timeouts={wall_clock_timeouts}"
                )
                if output_dirs:
                    print(f"Results saved to: {output_dirs[0]}")

                result = {
                    "benchmark": benchmark_name,
                    "agent": agent_name,
                    "num_success": num_success,
                    "num_total": num_total,
                    "success_rate": success_rate,
                    "gold_success_rate": gold_success_rate,
                    "judged_success_rate": judged_success_rate,
                    "judged_successes": judged_successes,
                    "skills_learned": skills_learned,
                    "failure_breakdown": {
                        "empty_trajectories": empty_trajectories,
                        "runtime_failures": runtime_failures,
                        "wall_clock_timeouts": wall_clock_timeouts,
                    },
                    "output_dir": output_dirs[0] if output_dirs else None,
                    "rewards": task_rewards
                }
                all_results.append(result)

                # Persist the aggregate, not only per-task trajectories and a
                # terminal printout, so interrupted/reviewed runs are auditable.
                if output_dirs:
                    import json
                    import os
                    summary_path = os.path.join(output_dirs[0], "evaluation_summary.json")
                    with open(summary_path, "w") as f:
                        json.dump(all_results, f, indent=2)

        # Print final skills summary
        if self.skill_config.get("enabled", True):
            self.print_skills_summary()

        return all_results


def main(config_path: str):
    """
    Run evaluation with online skill induction.

    Args:
        config_path: Path to YAML config file
        **kwargs: Additional arguments passed to evaluation
    """

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create evaluator
    evaluator = SkillInductionEvaluator(config_path)

    # Run evaluation with online skill induction
    results = evaluator.run_evaluation()

    print("\n" + "="*60)
    print("ONLINE SKILL INDUCTION COMPLETE")
    print("="*60)
    print("Skills were learned and applied during evaluation!")

    return results


if __name__ == "__main__":
    fire.Fire(main)
