## Decision

REFINE

## Justification

The hypotheses remain plausible, and the `scale=0.1` result is a meaningful exploratory signal. However, the mandatory criteria for PROCEED are not satisfied:

- Results are based on one seed, below the required three seeds per condition.
- Hard and Signed Top-2 have identical per-seed Task-0 and Final values at the original scale, raising an ablation-integrity concern.
- The proposed method’s contribution is not isolated from residual scaling or ordinary low-rank adaptation.
- Baseline budgets and sparse/dense comparisons are not fully matched.
- The analysis quality rating is exactly 4/10, meeting that criterion but not compensating for the failed seed and integrity criteria.

A PIVOT is unwarranted because the implementation passed key engineering checks and reducing the adapter scale substantially improved performance.

## Evidence

- Hard Top-2 improved from 86.17 to 90.06 Average and from 83.91 to 88.89 Final when scale changed to `0.1`.
- Its Forgetting decreased from 3.78 to 3.22.
- Hard Top-2 at `scale=0.1` trails CaRE by only 1.50 Average points and 0.81 Final points.
- All reported conditions have only `n=1`; no variance, confidence intervals, or reliable significance estimates are available.
- Hard and Signed Top-2 at the original scale both report Task-0 `88.42` and Final `83.91`.
- Sparse execution is approximately 41% slower than dense in the reported latency comparison.
- Strong load balancing lowers Forgetting but materially reduces Average accuracy, so its causal interpretation remains unresolved.

## Next Actions

1. Audit the Hard/Signed configurations, coefficient behavior, and logging to explain the identical results.
2. Add frozen-backbone/no-adapter, `scale=0`, and parameter-matched low-rank adapter baselines.
3. Re-run CaRE, Hard `scale=0.1`, Signed `scale=0.1`, and the new controls with at least 3–5 paired seeds and at least three fixed class orders.
4. Match training budgets, checkpoints, optimizers, parameter counts, and evaluation protocols across methods.
5. Separate hyperparameter selection from confirmation; do not reuse test results to select scale or balance settings.
6. Report paired effects with standard deviations and 95% confidence intervals, plus task-wise accuracy, BWT, old/new-class performance, routing diagnostics, and failure rates.
7. Compare sparse and dense variants under matched parameter, compute, and measured-latency budgets.
8. Keep the memory read-only until its benefit over simpler controls is demonstrated under longer continual-learning sequences.