# Running Mind2Web with PolySkill

PolySkill evaluates Mind2Web the way the paper does (§4.1): tasks are **executed on the
live web** via BrowserGym, and success is measured by an automatic **GPT-4.1 WebJudge**
(`webjudge_online_mind2web`, screenshot score threshold 3) — both during skill induction
and at test time. The dataset's recorded human actions are not replayed; they only define
the tasks.

You run the evaluation yourself: it needs your model API keys, reaches real third-party
websites, and its judge makes real LLM calls.

## 1. Get the task splits

The repo ships task metadata for the three settings under `data/mind2web/`
(see `data/mind2web/README.md` for provenance and caveats):

| Setting | File | Tasks |
|---|---|---|
| `cross-task` | `cross_task.json` | 177 |
| `cross-website` | `cross_website.json` | 142 |
| `cross-domain` | `cross_domain.json` | 694 |

To rebuild them (or apply your own start-URL overrides):

```bash
python scripts/prepare_mind2web.py                     # rebuild from HuggingFace
python scripts/prepare_mind2web.py --url-map my.json   # override start URLs
```

> **Counts note:** these are built from the openly redistributable Multimodal-Mind2Web
> test release, a subset of the original splits (252/177/912). If you have the full
> original test data, convert it to the same JSON schema and drop it in `data/mind2web/`.

## 2. Configure

`examples/configs/mind2web_polyskill_gpt4.yaml` is ready to use. The relevant knobs:

```yaml
skill_induction:
  judge_method: webjudge_online_mind2web   # the paper's judge
  judge_model: {provider: openai, name: gpt-4.1, temperature: 0.0, max_tokens: 4096}
  score_threshold: 3
  use_polymorphism: true
benchmarks:
  mind2web-cross-task:
    dataset: mind2web
    setting: cross-task        # cross-task | cross-website | cross-domain
    max_steps: 30
```

Set your keys (see `.env.example`): `OPENAI_API_KEY` (and/or `ANTHROPIC_API_KEY`,
`POLYSKILL_OSS_API_BASE`/`POLYSKILL_OSS_API_KEY` for the open-source models).

## 3. Run

```bash
python -m polyskill.experiments.mind2web.run_mind2web \
    --config examples/configs/mind2web_polyskill_gpt4.yaml \
    --setting cross-task \
    --model gpt-4.1
```

Tasks run sequentially (`threads: 1`) so each task can use skills induced from earlier
ones. Because live tasks have no gold reward, the reported **success rate is the
WebJudge verdict** (the harness prints both the raw environment reward — always 0 for
live tasks — and the judged SR; the judged SR is the paper's number).

## 4. Live-web caveats

- **Start URLs are best-effort guesses** from website names — verify them for the sites
  you evaluate (`data/mind2web/README.md`). Tasks whose sites have changed, geo-block, or
  bot-block will fail at navigation; the harness records the trajectory and the judge
  scores it failed, rather than crashing.
- **Cost:** each task = one browser rollout (up to `max_steps` model calls) plus judge
  calls (per-screenshot scoring + final verdict). Budget accordingly, especially for
  `cross-domain` (694 tasks).
- **Sites drift.** Mind2Web tasks were annotated in 2023; some tasks are no longer
  completable as written. This affects absolute numbers on live sites — expected for
  any live-web evaluation of this benchmark.
