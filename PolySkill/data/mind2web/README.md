# Mind2Web test splits (task metadata)

Task-level metadata for the three Mind2Web generalization settings, used by the
PolySkill harness for **live-web evaluation** (tasks are executed in the browser and
success is measured by the GPT-4.1 WebJudge, as in the paper — the dataset's recorded
actions are not used at test time).

| File | Setting | Tasks |
|---|---|---|
| `cross_task.json` | cross-task | 177 |
| `cross_website.json` | cross-website | 142 |
| `cross_domain.json` | cross-domain | 694 |

Each record: `{"task_id", "task", "website", "domain", "subdomain", "url"}`.

## Provenance & counts caveat

These files are built by `scripts/prepare_mind2web.py` from the openly redistributable
[`osunlp/Multimodal-Mind2Web`](https://huggingface.co/datasets/osunlp/Multimodal-Mind2Web)
release of the Mind2Web test data (metadata columns only — no HTML/screenshots).
That release is a **subset** of the original Mind2Web test splits (252 / 177 / 912 tasks);
tasks dropped there (mostly for screenshot-alignment issues) are absent here too. If you
obtain the full original test splits from the Mind2Web authors, convert them to the same
JSON schema and drop them in this directory — the harness reads whatever these files contain.

## `url` field caveat

Mind2Web websites are identified by name (e.g. `budget`, `careers.walmart`), not URL.
The `url` field is a **best-effort guess** (`https://www.<name>.com` heuristic). Live
sites change; verify/override the start URLs for the sites you evaluate — edit the JSON
or regenerate with `python scripts/prepare_mind2web.py --url-map your_map.json`.

## Attribution

Mind2Web: Deng et al., 2023 — "Mind2Web: Towards a Generalist Agent for the Web"
(https://osu-nlp-group.github.io/Mind2Web/), released under CC BY 4.0.
Multimodal test release: Zheng et al., 2024 (SeeAct) — `osunlp/Multimodal-Mind2Web`.
