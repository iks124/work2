#!/usr/bin/env python3
"""Run a small Mind2Web action-prediction sample with Bailian/DashScope."""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import json
import os
import pickle
import random
import re
import sys
import time
import zipfile
from pathlib import Path

import ijson
import lxml.etree
from openai import OpenAI


ROOT = Path(__file__).resolve().parent
MIND2WEB_SRC = ROOT / "Mind2Web" / "src"
sys.path.insert(0, str(MIND2WEB_SRC))

from data_utils.dom_utils import get_tree_repr, prune_tree  # noqa: E402


DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen3.6-35b-a3b"


PLANNER_SYSTEM_PROMPT = """You are a Mind2Web step planner. Given a web task and the actions already completed, predict the semantic hint for the next action.

Inputs:
- confirmed_task: the user's full task.
- previous_action_reprs: completed actions only, in chronological order. Each action_repr has the rough form "[role] visible text -> OPERATION[: value]".

Your job:
1. Infer current progress from previous_action_reprs.
2. Predict the next subgoal needed to continue the task.
3. Describe the target element semantically, not by candidate letter, backend node id, or any hidden id.
4. Predict the operation: CLICK, TYPE, or SELECT.
5. Predict the value only when the operation needs one. For CLICK, value must be empty.

Do not:
- Do not output candidate letters such as A, B, C, D, E.
- Do not output backend_node_id, node id, gold id, xpath, CSS selector, or coordinate.
- Do not claim to see current HTML or candidates.
- Do not include chain-of-thought or extra explanation.

Output exactly this JSON shape:
{
  "skill_context": "Current step oracle hint:\\n- Next subgoal: ...\\n- Target element role: ...\\n- Target visible text or label: ...\\n- Operation: CLICK|TYPE|SELECT.\\n- Value: ...\\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}

Formatting rules:
- Keep the field names and line order exactly as shown.
- Use an empty value rendered as "Value: ." for CLICK or unknown/no-value operations.
- If the target text is unavailable from history/task semantics, write "not available".
- Prefer the role and label style from Mind2Web action_reprs, such as searchbox, textbox, button, div, span, b, circle, svg."""


PLANNER_FEW_SHOTS = [
    {
        "input": {
            "confirmed_task": "Find a latest post with more than 10k upvotes in r/announcements community and upvote it.",
            "previous_action_reprs": [],
        },
        "output": {
            "skill_context": 'Current step oracle hint:\n- Next subgoal: interact with the searchbox labeled or described as "Search all of Reddit".\n- Target element role: searchbox.\n- Target visible text or label: Search all of Reddit.\n- Operation: CLICK.\n- Value: .\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices.'
        },
    },
    {
        "input": {
            "confirmed_task": "Find a latest post with more than 10k upvotes in r/announcements community and upvote it.",
            "previous_action_reprs": ["[searchbox]  Search all of Reddit -> CLICK"],
        },
        "output": {
            "skill_context": 'Current step oracle hint:\n- Next subgoal: interact with the searchbox labeled or described as "Search all of Reddit".\n- Target element role: searchbox.\n- Target visible text or label: Search all of Reddit.\n- Operation: TYPE.\n- Value: announcements.\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices.'
        },
    },
    {
        "input": {
            "confirmed_task": "Find a latest post with more than 10k upvotes in r/announcements community and upvote it.",
            "previous_action_reprs": [
                "[searchbox]  Search all of Reddit -> CLICK",
                "[searchbox]  Search all of Reddit -> TYPE: announcements",
            ],
        },
        "output": {
            "skill_context": 'Current step oracle hint:\n- Next subgoal: interact with the div labeled or described as "r/announcements".\n- Target element role: div.\n- Target visible text or label: r/announcements.\n- Operation: CLICK.\n- Value: .\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices.'
        },
    },
    {
        "input": {
            "confirmed_task": 'Follow the user "WarrenBuffett".',
            "previous_action_reprs": ["[textbox]  Search Stocktwits -> CLICK"],
        },
        "output": {
            "skill_context": 'Current step oracle hint:\n- Next subgoal: interact with the textbox labeled or described as "Search Stocktwits".\n- Target element role: textbox.\n- Target visible text or label: Search Stocktwits.\n- Operation: TYPE.\n- Value: @WarrenBuffett.\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices.'
        },
    },
    {
        "input": {
            "confirmed_task": "Get the weekend wedding first dance lessons in my home at zip 10005 for the beginner in Latin dance for a group of 3-4 people with no choreography or song preferences, and contact for prices on my phone number 5214586525.",
            "previous_action_reprs": [
                "[textbox]  Search on Thumbtack -> TYPE: wedding dance",
                "[b]  Wedding Dance -> CLICK",
            ],
        },
        "output": {
            "skill_context": 'Current step oracle hint:\n- Next subgoal: interact with the textbox labeled or described as "Zip code".\n- Target element role: textbox.\n- Target visible text or label: Zip code.\n- Operation: TYPE.\n- Value: 10005.\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices.'
        },
    },
]


def format_input_multichoice(
    sample: dict,
    candidate_ids: list[str],
    gt: str | int = -1,
    previous_k: int = 5,
    keep_html_brackets: bool = False,
) -> tuple[str, str, str, list[list[str]]]:
    dom_tree = lxml.etree.fromstring(sample["cleaned_html"])
    dom_tree = prune_tree(dom_tree, candidate_ids)
    tree_repr, id_mapping = get_tree_repr(
        dom_tree, id_mapping={}, keep_html_brackets=keep_html_brackets
    )
    candidate_nodes = dom_tree.xpath("//*[@backend_node_id]")
    choices = []
    for node in candidate_nodes:
        choices.append(
            [
                node.attrib["backend_node_id"],
                " ".join(
                    get_tree_repr(
                        node,
                        id_mapping=id_mapping,
                        keep_html_brackets=keep_html_brackets,
                    )[0].split()[:10]
                ),
            ]
        )

    gt = id_mapping.get(gt, -1)
    seq_input = (
        "Based on the HTML webpage above, try to complete the following task:\n"
        f"Task: {sample['confirmed_task']}\n"
        "Previous actions:\n"
    )
    if sample["previous_actions"]:
        for action in sample["previous_actions"][-previous_k:]:
            seq_input += f"{action}\n"
    else:
        seq_input += "None\n"
    seq_input += (
        "What should be the next action? Please select from the following choices "
        "(If the correct action is not in the page above, please select A. 'None of the above'):\n\n"
        "A. None of the above\n"
    )
    for idx, choice in enumerate(choices):
        seq_input += f"{chr(66 + idx)}. {choice[1]}\n"

    if gt == -1:
        seq_target = "A."
    else:
        gt += 1
        op = sample["operation"]["op"]
        value = sample["operation"]["value"]
        seq_target = f"{chr(65 + gt)}.\nAction: {op}\n"
        if op != "CLICK":
            seq_target += f"Value: {value}"
    return tree_repr, seq_input, seq_target, choices


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def iter_tasks(zip_path: Path, split_file: str | None, password: bytes):
    with zipfile.ZipFile(zip_path) as zf:
        names = [name for name in zf.namelist() if name.endswith(".json")]
        if split_file:
            names = [name for name in names if name == split_file or name.endswith(split_file)]
            if not names:
                raise FileNotFoundError(f"Split file not found in zip: {split_file}")
        for name in names:
            with zf.open(name, pwd=password) as fh:
                for task in ijson.items(fh, "item"):
                    task["_split_file"] = name
                    yield task


def task_to_action_samples(task: dict):
    action_reprs = task.get("action_reprs", [])
    for idx, action in enumerate(task.get("actions", [])):
        yield {
            "split_file": task.get("_split_file", ""),
            "website": task.get("website", ""),
            "confirmed_task": task.get("confirmed_task", ""),
            "annotation_id": task.get("annotation_id", ""),
            "previous_actions": action_reprs[:idx],
            "current_action_repr": action_reprs[idx] if idx < len(action_reprs) else "",
            "action_uid": action.get("action_uid", ""),
            "operation": action.get("operation", {}),
            "pos_candidates": action.get("pos_candidates", []),
            "neg_candidates": action.get("neg_candidates", []),
            "cleaned_html": action.get("cleaned_html", ""),
        }


def load_or_create_subset(
    zip_path: Path,
    split_file: str | None,
    password: bytes,
    sample_limit: int,
    subset_path: Path,
) -> list[dict]:
    tasks = []
    seen = set()
    for task in iter_tasks(zip_path, split_file, password):
        annotation_id = task.get("annotation_id")
        if not annotation_id or annotation_id in seen:
            continue
        seen.add(annotation_id)
        tasks.append(task)
        if sample_limit > 0 and len(tasks) >= sample_limit:
            break
    if str(subset_path) != "-":
        subset_path.parent.mkdir(parents=True, exist_ok=True)
        subset_path.write_text(json.dumps(tasks, ensure_ascii=False), encoding="utf-8")
    return tasks


def attach_ranks(sample: dict, ranks: dict | None, scores: dict | None) -> None:
    sample_id = f"{sample['annotation_id']}_{sample['action_uid']}"
    sample_ranks = ranks.get(sample_id, {}) if ranks else {}
    sample_scores = scores.get(sample_id, {}) if scores else {}
    fallback_rank = 0
    for candidates in (sample["pos_candidates"], sample["neg_candidates"]):
        for candidate in candidates:
            cid = candidate["backend_node_id"]
            candidate["rank"] = int(sample_ranks.get(cid, fallback_rank))
            candidate["score"] = float(sample_scores.get(cid, 0.0))
            fallback_rank += 1


def label_for(sample: dict, pos_id: str) -> tuple[str, str]:
    _, _, target_out, _ = format_input_multichoice(
        sample, [pos_id], pos_id, keep_html_brackets=True
    )
    selected, action = parse_output("Answer: " + target_out)
    return selected, action


def parse_output(text: str) -> tuple[str, str]:
    selected = re.search(r"(?:Answer:\s*)?([A-F])\.", text.strip())
    selected_option = selected.group(1) if selected else "A"
    action = re.search(r"Action:\s*(CLICK|SELECT|TYPE)", text)
    value = re.search(r"Value:\s*(.*)$", text, re.MULTILINE)
    action_text = action.group(1) if action else ""
    if value and value.group(1).strip():
        action_text = f"{action_text} {value.group(1).strip()}".strip()
    return selected_option, action_text


def extract_json_object(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(cleaned[start : end + 1])


def normalize_planner_skill_context(skill_context: str) -> str:
    lines = [line.rstrip() for line in skill_context.strip().splitlines()]
    if not lines:
        return ""
    normalized = "\n".join(lines)
    if "- Do not use any candidate letter or backend node id" not in normalized:
        normalized += (
            "\n- Do not use any candidate letter or backend node id from this hint; "
            "ground the hint in the HTML and choices."
        )
    return normalized


def build_planner_messages(sample: dict) -> list[dict]:
    messages = [{"role": "system", "content": PLANNER_SYSTEM_PROMPT}]
    for example in PLANNER_FEW_SHOTS:
        messages.append(
            {
                "role": "user",
                "content": (
                    "Now predict the next-step skill_context for this case.\n\n"
                    "Input:\n"
                    f"{json.dumps(example['input'], ensure_ascii=False, indent=2)}\n\n"
                    "Output:"
                ),
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": json.dumps(example["output"], ensure_ascii=False, indent=2),
            }
        )

    planner_input = {
        "confirmed_task": sample.get("confirmed_task", ""),
        "previous_action_reprs": sample.get("previous_actions", []),
    }
    messages.append(
        {
            "role": "user",
            "content": (
                "Now predict the next-step skill_context for this case.\n\n"
                "Input:\n"
                f"{json.dumps(planner_input, ensure_ascii=False, indent=2)}\n\n"
                "Output:"
            ),
        }
    )
    return messages


def plan_skill_context(client: OpenAI, sample: dict, model: str) -> tuple[str, str]:
    completion = client.chat.completions.create(
        model=model,
        messages=build_planner_messages(sample),
        max_tokens=220,
        temperature=0,
        extra_body={"enable_thinking": False},
    )
    raw_response = completion.choices[0].message.content or ""
    parsed = extract_json_object(raw_response)
    skill_context = normalize_planner_skill_context(str(parsed.get("skill_context", "")))
    return skill_context, raw_response


def action_repr_parts(action_repr: str) -> tuple[str, str, str]:
    match = re.match(r"\[(?P<role>[^\]]+)\]\s*(?P<label>.*?)\s*->\s*(?P<op>CLICK|TYPE|SELECT)(?::\s*(?P<value>.*))?$", action_repr)
    if not match:
        return "", action_repr.strip(), ""
    return (
        match.group("role").strip(),
        match.group("label").strip(),
        (match.group("value") or "").strip(),
    )


def skill_context_for(sample: dict, mode: str) -> str:
    if mode == "baseline":
        return ""

    role, label, repr_value = action_repr_parts(sample.get("current_action_repr", ""))
    op = sample.get("operation", {}).get("op", "")
    value = sample.get("operation", {}).get("value", "") or repr_value
    completed = sample.get("previous_actions", [])
    completed_lines = "\n".join(f"    - {action}" for action in completed[-5:]) or "    - None"
    value_line = value if value else ""
    label_phrase = f' labeled or described as "{label}"' if label else ""
    next_label_phrase = f' and label/text "{label}"' if label else ""

    if mode == "step_oracle_locator":
        return (
            "Current step oracle hint:\n"
            f"- Next subgoal: interact with the {role or 'target element'}"
            f"{label_phrase}.\n"
            f"- Target element role: {role or 'unknown'}.\n"
            f"- Target visible text or label: {label or 'not available'}.\n"
            f"- Operation: {op}.\n"
            f"- Value: {value_line}.\n"
            "- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
        )

    if mode == "ssgp_skill":
        return (
            "Relevant Skill Object:\n"
            "name: StatefulStepGroundedProtocolSkill\n"
            f"task_goal: {sample.get('confirmed_task', '')}\n"
            "current_state:\n"
            "  completed:\n"
            f"{completed_lines}\n"
            f"  next_subgoal: select the element that matches role \"{role or 'unknown'}\""
            f"{next_label_phrase}, then perform {op}.\n"
            "target_semantics:\n"
            f"  element_role: {role or 'unknown'}\n"
            f"  visible_text_or_label: {label or 'not available'}\n"
            f"  entity_or_value: {value_line}\n"
            "operation:\n"
            f"  type: {op}\n"
            f"  value: {value_line}\n"
            "positive_cues:\n"
            f"  - Prefer candidates whose role, placeholder, label, or visible text matches \"{label or role or 'the target'}\".\n"
            "  - Match the current next subgoal, not a past or future step in the task plan.\n"
            "negative_cues:\n"
            "  - Do not choose unrelated navigation, container, decorative, or promotional elements.\n"
            "  - Do not choose a search result or primary action button before the search/input step is complete.\n"
            "  - Do not output TYPE unless the operation.type is TYPE; do not output SELECT unless the target is a dropdown/select control.\n"
            "postcondition:\n"
            f"  - After this action, the page should be ready for the next step after: {sample.get('current_action_repr', '')}.\n"
            "leakage_rule:\n"
            "  - This skill intentionally does not provide candidate letters or backend node ids."
        )

    raise ValueError(f"Unknown skill mode: {mode}")


def build_messages(
    prompt_template: list[dict],
    seq_context: str,
    seq_in: str,
    skill_context: str = "",
) -> list[dict]:
    messages = copy.deepcopy(prompt_template)
    skill_block = (
        "\nRelevant skill / experience:\n"
        "Use this only as a semantic locator and action contract. It is not a candidate "
        "letter, backend_node_id, selector, or final answer; still ground the final "
        "answer in the HTML and listed choices.\n"
        f"{skill_context}\n"
        if skill_context
        else ""
    )
    messages[-1]["content"] = (
        f"'''\n{seq_context}\n'''\n{skill_block}\n{seq_in}\n"
        "Respond with exactly this format:\n"
        "Answer: <LETTER>.\n"
        "Action: <CLICK|SELECT|TYPE>\n"
        "Value: <text, only for TYPE or SELECT>"
    )
    return messages


def candidate_ids_for(sample: dict, top_k: int, num_choices: int) -> list[str]:
    pos = sorted(sample["pos_candidates"], key=lambda c: c.get("rank", 10**9))
    neg = sorted(sample["neg_candidates"], key=lambda c: c.get("rank", 10**9))
    pos_ids = [c["backend_node_id"] for c in pos if c.get("rank", 10**9) < top_k]
    neg_ids = [c["backend_node_id"] for c in neg if c.get("rank", 10**9) < top_k]
    if not pos_ids:
        return neg_ids[:num_choices]
    ids = [pos_ids[0]] + neg_ids[: max(0, num_choices - 1)]
    random.Random(42).shuffle(ids)
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="mind2web_data")
    parser.add_argument("--sample-limit", type=int, default=5)
    parser.add_argument("--limit", type=int, default=None, help="Optional action-step cap.")
    parser.add_argument("--split-file", default="test_domain/test_domain_0.json")
    parser.add_argument("--model", default=os.getenv("DASHSCOPE_MODEL", DEFAULT_MODEL))
    parser.add_argument("--planner-model", default=os.getenv("DASHSCOPE_PLANNER_MODEL", None))
    parser.add_argument("--base-url", default=os.getenv("DASHSCOPE_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--num-choices", type=int, default=5)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument(
        "--skill-mode",
        choices=["baseline", "step_oracle_locator", "ssgp_skill", "planner_history"],
        default="baseline",
    )
    parser.add_argument(
        "--subset-output",
        default="Mind2Web/data/bailian_test_domain_5_samples.json",
    )
    parser.add_argument("--output", default="results/mind2web_bailian_5_samples_full.json")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing output file by skipping completed sample ids.",
    )
    args = parser.parse_args()
    planner_model = args.planner_model or args.model

    load_env_file(ROOT / ".env.tools")
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("DASHSCOPE_API_KEY is not set. Put it in .env.tools or the environment.")

    data_dir = Path(args.data_dir)
    zip_path = data_dir / "test.zip"
    score_path = data_dir / "scores_all_data.pkl"
    with score_path.open("rb") as fh:
        candidate_results = pickle.load(fh)

    with (ROOT / "Mind2Web" / "src" / "action_prediction" / "llm_prompt.json").open(
        encoding="utf-8"
    ) as fh:
        prompt_template = json.load(fh)

    subset_path = Path(args.subset_output)
    tasks = load_or_create_subset(
        zip_path,
        args.split_file,
        b"mind2web",
        args.sample_limit,
        subset_path,
    )
    action_samples = [sample for task in tasks for sample in task_to_action_samples(task)]
    if args.limit is not None:
        action_samples = action_samples[: args.limit]
    print(
        f"Prepared {len(tasks)} task samples / {len(action_samples)} action steps "
        f"from {args.split_file}; subset={subset_path}",
        flush=True,
    )

    client = OpenAI(api_key=api_key, base_url=args.base_url)
    output_path = Path(args.output)

    def build_result(current_outputs: list[dict]) -> dict:
        return {
            "model": args.model,
            "planner_model": planner_model if args.skill_mode == "planner_history" else None,
            "base_url": args.base_url,
            "sample_limit": args.sample_limit,
            "action_limit": args.limit,
            "subset_path": str(subset_path),
            "skill_mode": args.skill_mode,
            "task_count": len(tasks),
            "count": len(current_outputs),
            "element_acc": sum(x["element_correct"] for x in current_outputs) / len(current_outputs)
            if current_outputs
            else 0,
            "action_acc": sum(x["action_correct"] for x in current_outputs) / len(current_outputs)
            if current_outputs
            else 0,
            "step_acc": sum(x["element_correct"] and x["action_correct"] for x in current_outputs)
            / len(current_outputs)
            if current_outputs
            else 0,
            "outputs": current_outputs,
        }

    def write_outputs(current_outputs: list[dict]) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(build_result(current_outputs), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    outputs = []
    completed_sample_ids = set()
    if args.resume and output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        outputs = list(existing.get("outputs", []))
        completed_sample_ids = {row.get("sample_id") for row in outputs if row.get("sample_id")}
        print(f"Loaded {len(outputs)} existing outputs from {output_path}", flush=True)

    def evaluate_one(sample: dict) -> dict | None:
        sample_id = f"{sample['annotation_id']}_{sample['action_uid']}"
        attach_ranks(sample, candidate_results.get("ranks"), candidate_results.get("scores"))
        ids = candidate_ids_for(sample, args.top_k, args.num_choices)
        if len(ids) < 2:
            return None
        pos_ids = {c["backend_node_id"] for c in sample["pos_candidates"]}
        seq_context, seq_in, _, choices = format_input_multichoice(
            sample, ids, -1, keep_html_brackets=True
        )
        planner_raw_response = ""
        last_error = None
        skill_context = ""
        completion = None
        for attempt in range(3):
            try:
                if args.skill_mode == "planner_history":
                    skill_context, planner_raw_response = plan_skill_context(client, sample, planner_model)
                else:
                    skill_context = skill_context_for(sample, args.skill_mode)
                messages = build_messages(prompt_template, seq_context, seq_in, skill_context)
                completion = client.chat.completions.create(
                    model=args.model,
                    messages=messages,
                    max_tokens=80,
                    temperature=0,
                    extra_body={"enable_thinking": False},
                )
                break
            except Exception as exc:  # API/network retries for long full-set runs.
                last_error = exc
                if attempt == 2:
                    if args.skill_mode != "planner_history":
                        raise
                    planner_raw_response = f"PLANNER_ERROR: {type(exc).__name__}: {exc}"
                    skill_context = ""
                    messages = build_messages(prompt_template, seq_context, seq_in, skill_context)
                    completion = client.chat.completions.create(
                        model=args.model,
                        messages=messages,
                        max_tokens=80,
                        temperature=0,
                        extra_body={"enable_thinking": False},
                    )
                    break
                time.sleep(2 * (attempt + 1))
        response_text = completion.choices[0].message.content or ""
        pred_letter, pred_action = parse_output(response_text)
        pred_idx = ord(pred_letter) - ord("B")
        pred_backend_id = choices[pred_idx][0] if 0 <= pred_idx < len(choices) else None
        target_id = next(iter(pos_ids), None)
        _, target_action = label_for(sample, target_id) if target_id else ("A", "")
        return {
            "sample_id": sample_id,
            "split_file": sample["split_file"],
            "website": sample["website"],
            "task": sample["confirmed_task"],
            "target_backend_id": target_id,
            "target_action": target_action,
            "prediction_backend_id": pred_backend_id,
            "prediction_action": pred_action,
            "skill_mode": args.skill_mode,
            "skill_context": skill_context,
            "planner_raw_response": planner_raw_response,
            "raw_response": response_text,
            "element_correct": pred_backend_id in pos_ids,
            "action_correct": pred_action == target_action,
        }

    remaining_samples = [
        sample
        for sample in action_samples
        if f"{sample['annotation_id']}_{sample['action_uid']}" not in completed_sample_ids
    ]
    workers = max(1, args.workers)

    if workers == 1:
        result_iter = (evaluate_one(sample) for sample in remaining_samples)
    else:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)
        futures = [executor.submit(evaluate_one, sample) for sample in remaining_samples]
        result_iter = (future.result() for future in concurrent.futures.as_completed(futures))

    try:
        for row in result_iter:
            if row is None:
                continue
            outputs.append(row)
            if len(outputs) % max(1, args.progress_every) == 0 or len(outputs) == len(action_samples):
                print(
                    f"[{len(outputs)}/{len(action_samples)}] "
                    f"element_acc={build_result(outputs)['element_acc']:.4f} "
                    f"action_acc={build_result(outputs)['action_acc']:.4f} "
                    f"step_acc={build_result(outputs)['step_acc']:.4f}",
                    flush=True,
                )

            if args.resume and len(outputs) % 25 == 0:
                write_outputs(outputs)
    finally:
        if workers > 1:
            executor.shutdown(wait=True, cancel_futures=True)

    result = build_result(outputs)
    write_outputs(outputs)
    print(json.dumps({k: result[k] for k in ["count", "element_acc", "action_acc", "step_acc"]}, indent=2))
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
