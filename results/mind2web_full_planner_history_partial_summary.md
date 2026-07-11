# Mind2Web full planner_history run partial summary

Run setting:

- Script: `run_mind2web_bailian_5.py`
- Skill mode: `planner_history`
- Model: `qwen3.6-35b-a3b`
- Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- Workers: 8
- Candidate setting: `top_k=50`, `num_choices=5`
- Completed date: 2026-07-10

The run stopped when starting `test_website/test_website_0.json` because Bailian/DashScope returned:

```text
BadRequestError: Arrearage
Access denied, please make sure your account is in good standing.
```

Completed splits:

| Split | Count | Element Acc | Action Acc | Step Acc | Planner Errors |
|---|---:|---:|---:|---:|---:|
| test_domain_0 | 660 | 0.434848 | 0.610606 | 0.350000 | 0 |
| test_domain_1 | 679 | 0.471281 | 0.683358 | 0.407953 | 0 |
| test_domain_2 | 592 | 0.412162 | 0.626689 | 0.336149 | 0 |
| test_domain_3 | 746 | 0.441019 | 0.588472 | 0.378016 | 0 |
| test_domain_4 | 614 | 0.438111 | 0.640065 | 0.371336 | 1 |
| test_domain_5 | 580 | 0.410345 | 0.648276 | 0.356897 | 0 |
| test_domain_6 | 615 | 0.497561 | 0.653659 | 0.429268 | 0 |
| test_domain_7 | 671 | 0.421759 | 0.609538 | 0.345753 | 0 |
| test_domain_8 | 687 | 0.403202 | 0.641921 | 0.360990 | 0 |
| test_domain_9 | 67 | 0.477612 | 0.701493 | 0.388060 | 0 |
| test_task_0 | 830 | 0.479518 | 0.661446 | 0.421687 | 0 |
| test_task_1 | 799 | 0.515645 | 0.672090 | 0.464330 | 0 |
| test_task_2 | 464 | 0.463362 | 0.642241 | 0.392241 | 0 |

Aggregate completed results:

| Group | Count | Element Acc | Action Acc | Step Acc | Planner Errors |
|---|---:|---:|---:|---:|---:|
| cross-domain | 5911 | 0.437320 | 0.633565 | 0.371172 | 1 |
| cross-task | 2093 | 0.489728 | 0.661252 | 0.431438 | 0 |
| completed total | 8004 | 0.451024 | 0.640805 | 0.386932 | 1 |

Not completed:

- `test_website/test_website_0.json`
- `test_website/test_website_1.json`

Resume command after the Bailian account is available:

```bash
python3 - <<'PY'
import subprocess, sys
splits = [
    "test_website/test_website_0.json",
    "test_website/test_website_1.json",
]
for split in splits:
    tag = split.replace("/", "_").replace(".json", "")
    out = f"results/mind2web_full_planner_history_{tag}.json"
    subprocess.run([
        sys.executable, "run_mind2web_bailian_5.py",
        "--sample-limit", "0",
        "--split-file", split,
        "--skill-mode", "planner_history",
        "--output", out,
        "--subset-output", "-",
        "--workers", "8",
        "--progress-every", "100",
        "--resume",
    ], check=True)
PY
```
