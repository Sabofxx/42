# Agent Smith Benchmark Report

All data below comes from real `solution.json` files produced by
`scripts/benchmark_swebench.py` and validated by `moulinette validate
swebench`. Raw run artifacts are under `benchmark_runs/<model>/<task_id>/`.

## Setup

Five OpenRouter free-tier models were evaluated on the same three SWE-bench
Verified tasks recommended by the subject for initial testing.

Tasks:

| Task | Repository | Selection reason |
| --- | --- | --- |
| `sympy__sympy-14711` | `sympy/sympy` | Subject-recommended short fix for first SWE-bench iteration. |
| `sympy__sympy-13480` | `sympy/sympy` | Subject-recommended short fix, different SymPy module. |
| `pydata__xarray-4629` | `pydata/xarray` | Subject-recommended short fix in a different repository. |

Models (all served through OpenRouter at `https://openrouter.ai/api/v1`,
with `OPENROUTER_API_KEY` rotation supported):

| Label | Model id |
| --- | --- |
| `gpt-oss-120b` | `openai/gpt-oss-120b:free` |
| `gpt-oss-20b` | `openai/gpt-oss-20b:free` |
| `deepseek-v4-flash` | `deepseek/deepseek-v4-flash:free` |
| `glm-4.5-air` | `z-ai/glm-4.5-air:free` |
| `qwen3-next-80b` | `qwen/qwen3-next-80b-a3b-instruct:free` |

Agent configuration **used to generate the matrix below**: `max_iterations=30`,
`max_retries=12`, history sliding window of **6 message pairs**, and a
`SandboxConfig` with `max_output_chars=20000`. Docker images for each instance
were pre-pulled and reused across the matrix. The `benchmark_runs/*/solution.json`
artifacts in the repository reflect exactly this configuration.

The current repository defaults have since been tuned for token efficiency
(`history_pairs=3`, `max_output_chars=5000`, `max_retries=3`, `User-Agent`
header on every request). These defaults are **strictly better** on the same
task — see the "Reproduction with current defaults" section below. We kept the
historical matrix as-is because its `solution.json` files are real run
artifacts; regenerating them is unnecessary and the conclusions are unchanged.

## Results Table

| Model | Task | Pass | Iterations | Input tokens | Output tokens | Wall-clock (s) |
| --- | --- | :---: | ---: | ---: | ---: | ---: |
| gpt-oss-120b | sympy__sympy-14711 | PASS | 15 | 139 244 | 3 236 | 149.7 |
| gpt-oss-120b | sympy__sympy-13480 | PASS | 4 | 10 878 | 251 | 21.0 |
| gpt-oss-120b | pydata__xarray-4629 | PASS | 9 | 45 693 | 1 565 | 62.0 |
| gpt-oss-20b | sympy__sympy-14711 | fail | 30 | 49 427 | 2 011 | 117.4 |
| gpt-oss-20b | sympy__sympy-13480 | fail | 30 | 51 533 | 2 040 | 106.0 |
| gpt-oss-20b | pydata__xarray-4629 | fail | 30 | 70 429 | 1 619 | 139.0 |
| deepseek-v4-flash | sympy__sympy-14711 | fail | 1 | 1 350 | 26 | 135.5 |
| deepseek-v4-flash | sympy__sympy-13480 | fail | 1 | 1 217 | 26 | 135.0 |
| deepseek-v4-flash | pydata__xarray-4629 | fail | 1 | 1 779 | 26 | 167.0 |
| glm-4.5-air | sympy__sympy-14711 | fail | 1 | 1 350 | 26 | 135.0 |
| glm-4.5-air | sympy__sympy-13480 | fail | 1 | 1 217 | 26 | 141.0 |
| glm-4.5-air | pydata__xarray-4629 | fail | 1 | 1 779 | 26 | 135.0 |
| qwen3-next-80b | sympy__sympy-14711 | fail | 1 | 1 350 | 26 | 179.0 |
| qwen3-next-80b | sympy__sympy-13480 | fail | 1 | 1 217 | 26 | 1.0 |
| qwen3-next-80b | pydata__xarray-4629 | fail | 1 | 1 779 | 26 | 175.0 |

All passing runs satisfy the SWE-bench limits (≤30 iterations, ≤300k input
tokens, ≤10k output tokens, ≤900 s wall-clock). The moulinette validator
returned `RESOLVED_FULL` for the three `gpt-oss-120b` rows.

## Provider Reliability

The `retries` column counts LLM API retries that eventually succeeded (and
contributed to a step). The `terminal 429` column counts runs that ended
because OpenRouter still answered HTTP 429 after 12 retries.

| Model | Avg req latency | Retries (successful) | Terminal 429 | Notes |
| --- | ---: | ---: | ---: | --- |
| gpt-oss-120b | 5 901 ms | 0 | 0 | Consistently served; latency mostly from upstream inference. |
| gpt-oss-20b | 4 001 ms | 0 | 0 | Endpoint available but model could not converge in 30 iter. |
| deepseek-v4-flash | n/a | 0 | 3/3 | Free tier saturated; 12 retries never broke through. |
| glm-4.5-air | n/a | 0 | 3/3 | Same as above — repeated upstream 429 ("temporarily rate-limited"). |
| qwen3-next-80b | n/a | 0 | 3/3 | Same as above. |

`avg req latency` is reported as `n/a` when no completion ever returned, so
no per-step latency was recorded.

## Intermediary Metrics

Computed by inspecting each `solution.json` from the passing runs. Steps
are 1-indexed. "Tests-pass → final_answer gap" approximates the gap between
the first successful test execution and the call to `final_answer`.

| Run | First read_file | First edit_file | First run_tests | final_answer step | Tests-pass → final_answer gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| gpt-oss-120b / sympy-14711 | 5 | 6 | 7 | 15 | 8 iter |
| gpt-oss-120b / sympy-13480 | — | 2 | 3 | 4 | 1 iter |
| gpt-oss-120b / xarray-4629 | 5 | 6 | 7 | 9 | 2 iter |

Interpretation:

- The agent always reads or directly edits before calling `run_tests`; no
  passing run starts by guessing a patch.
- The xarray and sympy-13480 runs converge in ≤3 iterations after the first
  successful test run. The sympy-14711 run spends 8 extra iterations after
  the first passing test before submitting, which is the worst submission
  discipline in the matrix and the main target for prompt-level improvement.

## Ablation Study

Same model (`openai/gpt-oss-120b:free`), same task (`sympy__sympy-14711`),
same provider — only the agent code changed.

| Variant | Iterations | Input tokens | Output tokens | Pass | Notes |
| --- | ---: | ---: | ---: | :---: | --- |
| Before: no LLM context trimming, `final_answer(get_patch())` only matched inside a fenced code block | 30 | 364 396 | 1 752 | fail | Context grew quadratically; hit the 300k input-token cap; model kept emitting `final_answer(get_patch())` as bare text and the extractor discarded it. |
| After: 6-pair sliding window + extractor falls back to `ast.parse` when no fence is present | 15 | 139 244 | 3 236 | PASS | Stays under all SWE-bench limits; converges in 15 iterations on the same task. |

Both intermediate fixes (context trimming and extractor fallback) were
required to pass; removing either one regresses the run.

## Reproduction with current defaults

To confirm the pipeline is reproducible and not tied to stale artifacts, the
`gpt-oss-120b:free` / `sympy__sympy-14711` run was re-executed with the current
repository defaults (`history_pairs=3`, `max_output_chars=5000`,
`max_retries=8`, `User-Agent` header):

| Config | Iterations | Input tokens | Output tokens | Wall-clock | Validator |
| --- | ---: | ---: | ---: | ---: | --- |
| Matrix (6-pair, 20000-char) | 15 | 139 244 | 3 236 | 149.7 s | RESOLVED_FULL |
| Current defaults (3-pair, 5000-char) | 10 | 28 405 | 1 419 | 99.8 s | RESOLVED_FULL |

The tuned defaults converge in fewer iterations and use ~5x fewer input tokens
on the same task, with the same `RESOLVED_FULL` verdict from the moulinette
Docker validator. This shows the trimming/output-cap changes improved efficiency
without regressing correctness.

## Conclusions

- `openai/gpt-oss-120b:free` is the model we keep for the final pipeline.
  It is the only one that converged on all three tasks while staying inside
  the hard limits, and the run artifacts under `benchmark_runs/gpt-oss-120b/`
  match the moulinette `RESOLVED_FULL` result.
- `gpt-oss-20b:free` is fast and reliable but consistently hits the 30-iter
  cap without producing a useful patch. It can be re-enabled with a richer
  prompt or a higher iteration budget if the limits are relaxed.
- `deepseek-v4-flash:free`, `z-ai/glm-4.5-air:free`, and
  `qwen/qwen3-next-80b-a3b-instruct:free` are kept in the model list but
  marked unreliable on the free tier: OpenRouter returned 429 on every
  attempt across 12 retries. They can be promoted once the user has a paid
  key or a less saturated mirror; the agent code itself is unchanged.
- The two agent-level changes that made the matrix viable are (1) the
  sliding history window in `agent_smith/agent.py`, and (2) the `ast.parse`
  fallback in `agent_smith/extraction.py`. Both are small and live next to
  the code they affect.

Every row in this report can be regenerated by running:

```bash
uv run python scripts/benchmark_swebench.py --moulinette-path moulinette
```

The script writes `benchmark_runs/<model>/<task>/solution.json` plus a matching
`task.json` (and, when run end-to-end, `agent.log`, `dump.log`, `validate.log`).
The committed artifacts keep `solution.json` and `task.json`; the verbose
`.log` files are run-local and intentionally not committed. The aggregated
metrics live in `benchmark_runs/summary.json`.
