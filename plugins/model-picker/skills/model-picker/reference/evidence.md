# Model Picker Evidence Notes

Audit snapshot: **2026-09-13**. Companion to [models-condensed.md](models-condensed.md). These are retrieved-source observations, not new benchmark runs. The only local experiment was the offline clodex mapping/serialization check in I1. Linked pages are live and may later differ from this snapshot.

## Evidence contract

- **P — Provider documentation:** authoritative for that provider's stated functionality, prices, and access conditions; positioning is not independent proof of superiority.
- **E — Provider-run evaluation:** measured under the provider's setup. Retain its task, configuration, accounting, and limitations.
- **T — Third-party evaluation:** measured by an evaluator other than the model provider. This does not certify absence of all commercial relationships.
- **V — Commercial vendor evaluation:** CodeRabbit's specifically approved supporting evidence. Not an independent, matched model leaderboard.
- **U — Unestablished:** the audit did not establish a suitable comparison. This is neither a negative capability finding nor proof no evidence exists elsewhere.

Do not transform a score ratio into “percent better at coding,” a rating into a percentage, an aggregate cost into coding cost, or a token rate into measured cost per completed task. Do not infer live backend behavior from offline serialization. Where effort, dataset, repetitions, or confidence intervals are absent, preserve the gap.

## P1: Claude pricing and retention

Sources:
- [Model and feature pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)
- [Haiku model documentation](https://www.anthropic.com/claude/haiku)

Observed standard base input/cache-read/output rates per million tokens:

| Model | Input | Cache read | Output |
|---|---:|---:|---:|
| Haiku 4.5 | $1 | $0.10 | $5 |
| Sonnet 5 | $2 | $0.20 | $10 |
| Opus 5 | $5 | $0.50 | $25 |
| Fable 5.1 | $10 | $0.25 | $50 |

Claude 5-minute cache writes are 1.25× input; 1-hour writes are 2×. Fable 5.1 cache hits cost 0.025× base input rather than the other listed models' 0.1×. Batch input/output prices are 50% lower; standard prompt-caching multipliers apply. Opus fast mode base rates are $10/$50, separate from effort.

Sonnet 5's $2/$10 rates became standard rather than increasing after the introductory period. Sonnet/Opus/Fable have 1M context at standard token rates; Haiku has 200K. The pricing docs describe a newer tokenizer for Claude 4.7 and later, approximately 30% more tokens for the same text with workload variation. Sonnet's release documentation gives a content-dependent 1.0–1.35× range; these are not guaranteed billing ratios.

Fable 5.1 requires 30-day data retention and is not available under ZDR arrangements unless expressly authorized by Anthropic. Do not simplify the exception away. API prices do not describe subscription quotas or imply the same task token usage.

## P2: OpenAI model documentation

Sources:
- [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [GPT-5.6 Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra)
- [GPT-5.6 Sol](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)

Observed standard input/cache-read/output rates: Luna $0.20/$0.02/$1.20; Terra $2/$0.20/$12; Sol $4/$0.40/$20; Astra $10/$1/$50. Astra documentation also lists cache writes at $12.50/M. Requests above 272K input tokens incur 2× input and 1.5× output pricing for the full request; check route-specific cache details. No batching exemption was established.

Each page reports 1,050,000 total context tokens, 922,000 maximum input, and 128,000 maximum output. Capacity is not proof of reliable retrieval at that length. No verified MRCR length-specific cutoff was recovered for Luna or Sol in this audit.

Luna/Terra/Sol support none/low/medium/high/xhigh/max, default medium. Astra supports low/medium/high/xhigh/max, not none; the retrieved Astra model-page summary did not establish an API default. Sol's current price is available **at least through November 21, 2026**; a guaranteed subsequent rate was not established. “Ultra” was not a documented model effort level.

## P3: Claude effort and task positioning

Sources:
- [Effort](https://platform.claude.com/docs/en/build-with-claude/effort)
- [Sonnet 5 prompting](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)
- [Sonnet 5 release and evaluations](https://www.anthropic.com/news/claude-sonnet-5)
- [Opus 5 release and evaluations](https://www.anthropic.com/news/claude-opus-5)
- [Fable 5.1 migration](https://platform.claude.com/docs/en/models/fable-5-1/migration-guide)
- [Haiku 4.5 release](https://www.anthropic.com/news/claude-haiku-4-5)

Sonnet/Opus/Fable support low/medium/high/xhigh/max, with high the documented default. Haiku is not in the newer effort-parameter compatibility list; it uses the older thinking control. Do not invent quality guarantees for particular manual thinking budgets.

Effort is a behavioral control, not a guaranteed token budget, runtime, or correctness level. The effort docs start Opus/Fable at high and advise measuring step-downs; E1 separately discusses low-effort cost optimization. These are different objectives, not a contradiction to hide.

**Sonnet correction:** “With thinking disabled, the model is less likely to reach for tools or consider searching; if you rely on tool calls with thinking off, add an explicit nudge in the system prompt.” Tools are not prohibited by disabling thinking. Sonnet defaults to adaptive thinking; manual extended thinking is not supported. The provider positions it for coding, agentic tasks, structured extraction, and predictable pipelines.

**Review caveat:** Anthropic explains that conservative review prompts can reduce Sonnet's reported recall because it more literally filters findings to the specified bar. This is the provider's explanation, not independent proof that every observed recall drop is a harness effect.

**Security caveat:** Sonnet's reported failure to develop a full working exploit concerns a particular Firefox evaluation. It does not establish universal refusal, zero defensive capability, or a reason to exclude all Claude models from threat modeling or security review. Opus documentation separately discusses capabilities and safeguards; neither should be collapsed into one “security” score.

## E1: Anthropic cost and intelligence evaluations

Source: [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence).

**Provenance:** provider-run evaluation, not an independent replication. Preserve task and configuration; do not merge its SWE-bench results with another evaluator's harness. The retrieved results do not supply a complete matched all-eight-model comparison. Repetition counts and confidence intervals are not recorded in this audit's extracted comparison tables.

### SWE-bench Pro

| Configuration | Pass rate | Cost per solved task |
|---|---:|---:|
| Sonnet 5 default | 77.4% | $0.84 |
| Opus 5 low | 84.0% | $0.25 |
| Fable 5.1 low | 88.6% | $0.54 |
| Opus 5 default | 91.7% | $1.01 |
| Fable 5.1 default | 92.1% | $1.19 |

The source describes default Opus/Fable results as within noise. Derived arithmetic: Opus low minus Sonnet default = 6.6 percentage points; 1 − 0.25/0.84 ≈ 70% lower solved-task cost. Fable low minus Opus low = 4.6 points; 0.54/0.25 = 2.16× solved-task cost. These are specific to this evaluation, not general coding differences.

### DeepResearch Bench II

| Configuration | Score | Cost per task |
|---|---:|---:|
| Sonnet 5 default | 56% | $1.20 |
| Opus 5 default | 71% | $6.71 |
| Fable 5.1 low | 66% | $4.66 |
| Fable 5.1 default | 65% | $7.12 |

Do not label these costs “per solved task.” They demonstrate research overlap and effort tradeoffs among these configurations, not superiority over GPT models absent from the table.

### Delegation is conditional

The reported Fable 5.1 plus 25 concurrent Sonnet 5 worker experiment processed a **21.6M-token corpus**, too large for one context window. Relative to solo Fable high, the source reports **47–55% savings**, **10–12 points lower accuracy**, and **2.3 hours versus 15–20 hours** wall time. Do not generalize it to all orchestration or to untested Sol/Luna and Opus/Haiku pairings.

The same source recommends comparing a stronger single model at low effort before adding an advisor/orchestrator. Delegation is not automatically cheaper, faster, or equally accurate.

## T1: Artificial Analysis v4.3

Sources:
- [Index composition, cost accounting, and scope](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index)
- [Luna max / Sonnet max](https://artificialanalysis.ai/models/comparisons/gpt-5-6-luna-vs-claude-sonnet-5)
- [Terra max / Sol max](https://artificialanalysis.ai/models/comparisons/gpt-5-6-terra-vs-gpt-5-6-sol)
- [Sol max / Opus max](https://artificialanalysis.ai/models/comparisons/gpt-5-6-sol-vs-claude-opus-5)
- [Opus max / Fable max](https://artificialanalysis.ai/models/comparisons/claude-opus-5-vs-claude-fable-5-1)
- [Astra max / Fable max](https://artificialanalysis.ai/models/comparisons/gpt-6-astra-vs-claude-fable-5-1)
- [Sonnet configuration and cost definition](https://artificialanalysis.ai/models/claude-sonnet-5)
- [Evaluator background](https://artificialanalysis.ai/about)
- [General methodology](https://artificialanalysis.ai/methodology)

The main reference's T1 table is transcribed from these comparison pages, not newly measured. Model settings: GPT max; Claude Adaptive Reasoning, Max Effort; Fable additionally Default Fallback. A default-fallback result is a configuration result, not proof every task was handled without a fallback.

Index v4.3 contains ten evaluations: AA-Briefcase, GDPval-AA v2, AutomationBench-AA, Terminal-Bench v4.0, SciCode, Humanity's Last Exam, GDP.pdf, CritPt, AA-Omniscience, and AA-LCR v1.1. Four categories each contribute 25%: agents, coding, general capability, scientific reasoning.

**Weighted cost/task:** each evaluation's input, cache-hit, cache-write, reasoning, and answer-token costs are divided by its task count and weighted by the Index weighting. This is different from the total cost of running the Index and from any one benchmark's cost per successful task. Sonnet's page explicitly labels $5.09 as a weighted average per Index task; its aggregate Index execution cost is a separate metric.

**AA-LCR v1.1:** long-form documents approximately 10K–100K tokens, measured using cl100k_base. Its score is not an MRCR needle-retrieval result and cannot establish 512K–1M reliability. GDPval-AA is a rating, not percentage success. Small task-score differences without uncertainty estimates are not decisive superiority claims.

**Comparability limits:** use only the same version and displayed settings. The audit did not recover a complete task-level account of every harness, repeated-run count, or confidence interval behind each comparison row. Do not claim matched live clodex performance or statistical significance. Haiku's non-reasoning configuration was not mixed into the seven-model max-effort table.

**Independence limits:** AA calls itself an independent benchmarking company. Reviewed About/methodology pages did not disclose enough to certify absence of all paid relationships or evaluation-specific sponsorship. No specific sponsorship for these retrieved comparison rows was established in this audit. Keep the T provenance label and this limitation; do not claim “certified unbiased.” Use original task results, not commentary, as evidence.

## T2: Effort and latency comparison

Source: [Luna max / Terra medium](https://artificialanalysis.ai/models/comparisons/gpt-5-6-luna-vs-gpt-5-6-terra-medium).

At the retrieved snapshot: Luna max Index v4.3 = 38; Terra medium = 30. Both report $0.18 weighted cost/task. Time to first token is 121.85s versus 1.82s. These are measurements of particular configurations, not latency guarantees. They show why an aggregate score/cost tie does not settle an interactive-use recommendation. They do not establish a task-specific coding-quality comparison.

## V1: CodeRabbit Sol and Terra

Source: [OpenAI GPT-5.6 Sol and Terra: Benchmark](https://www.coderabbit.ai/blog/gpt-5-6-sol-and-terra-benchmark), published July 9, 2026.

**Status:** user-authorized commercial supporting evidence. CodeRabbit's proprietary review evaluation is not the independent-evidence category. Keep its own experiments separate from external benchmark summaries on the same page.

| Metric | Sol 5.6 | Terra 5.6 |
|---|---:|---:|
| Actionable pass / expected issue points | 69/99 (69.7%) | 53/101 (52.5%) |
| Pass full | 74/99 (74.7%) | 58/101 (57.4%) |
| Reported precision | 31.6% | 35.7% |
| Comments | 231 | 143 |
| Nitpicks | 61 | 21 |

**Definitions:** pass credits expected issues found actionably; pass full credits the broader valid-finding stream. Precision concerns the reported review-comment stream, not overall model accuracy. Comment/nitpick counts and issue-point denominators are different quantities. Do not equate 99/101 issue points with the number of pull requests, infer precision from pass/comments, or combine actionable and full-stream metrics.

**Limits:** exact effort, full dataset size, repetitions, and CIs were not established from the retrieved report. Sol/Terra denominators differ. No reliable measured per-task cost comparison was established. The later Fable report distinguishes the Sol raw-output results from its own processed pipeline. Do not assign Sol low/medium recommendations to these unspecified-effort results or treat precision as measured at the same pipeline stage across publications.

## V2: CodeRabbit Sonnet

Source: [Claude Sonnet 5 review](https://www.coderabbit.ai/blog/claude-sonnet-5-review), retrieved September 13, 2026; publication date not established in the audit extract.

Reported Sonnet 5 bug catch is approximately **50–51%** with precision approximately **38–40%**. These are reported ranges, not a single paired configuration. The article compares them with its production baseline and a prior Sonnet 4.6 snapshot; those are not a matched all-current-model leaderboard.

The source describes fixed pull requests with known bugs. Exact evaluation size, denominators, CIs, and a complete configuration-to-metric mapping were not established. Its separate analysis of **470 open-source pull requests** is contextual material, not an established size for this model evaluation; do not use it as the benchmark denominator.

The source says maximum thinking roughly doubled cost without meaningfully more bug findings. Exact dollar costs and a matched configuration table were not established; keep this qualitative/source-attributed rather than inventing precise savings or declaring max universally wasteful.

## V3: CodeRabbit Opus

Source: [Claude Opus 5 benchmarks for AI code review](https://www.coderabbit.ai/blog/opus-5-model-review), published July 24, 2026.

Approximately 100 error patterns from verified issues in real open-source pull requests; three runs per configuration, results averaged. Configurations include junior-reviewer medium, senior-reviewer high, and senior-reviewer x-high. Profile and effort both matter; do not attribute every difference to effort alone.

The reported **senior-reviewer x-high** configuration has **55.2% actionable pass**, **39.3% actionable precision**, **28.6% full-stream precision**, and **92 nitpicks**. The production baseline has different results and is an ensemble/lane comparison, not one equivalent model. Outputs undergo verification, deduplication, and filtering.

No explicit CIs or direct cost-per-task measurements were established. The token-usage figures in the report are not enough to reconstruct cost per successful task without cache/attempt accounting. Sonnet and other publication comparisons are different snapshots, not clean paired trials.

## V4: CodeRabbit Fable

Source: [Fable 5.1 model review](https://www.coderabbit.ai/blog/fable-5-1-model-review), published September 1, 2026.

**Within-study comparison:** same **45 tasks**, **105 known-issue points**; labels “Low” and “High” refer to the report's reasoning configurations. Their exact mapping to public API effort was not established by this audit.

| Fable 5.1 setting | Recall | Precision | Final comments | Mean latency/task |
|---|---:|---:|---:|---:|
| Low | 64/105 = 61.0% | 37.3% | 166 | 18:38 |
| High | 57.1% | 36.4% | 165 | 21:36 |

Recall credits a known issue with at least one valid comment. Precision is the share of final comments marked valid after the pipeline; comment totals are post-processing. Latency is an average per task, not total evaluation time. The source says reliable input/output token totals were not recorded; no measured review-cost comparison should be manufactured.

Higher reasoning took 2:58 longer per task and did not improve the reported recall/precision in this experiment. Without uncertainty estimates, do not claim a universal regression or optimal API effort.

**Cross-snapshot warning:** Fable 5.1 used an updated review pipeline. The source explicitly says not to read its comparison table as one leaderboard. Even sharing 105 known-issue points with Fable 5 does not remove the pipeline confound. Opus and Sol figures come from their own setups. Fable 5 is outside this reference's model scope; its scores must not be substituted for Fable 5.1.

## I1: Clodex effort verification

Inspected local package: **@bman654/clodex 2.11.6**, with installed **@ai-sdk/openai 4.0.11**. Inspected upstream revision: **2f4c7f5fcb5c07a0fec81506111f428706413e50**.

Pinned sources:
- [Model-family and effort mapping](https://github.com/bman654/clodex/blob/2f4c7f5fcb5c07a0fec81506111f428706413e50/src/provider-factory.ts#L587-L648)
- [OpenAI capability/default](https://github.com/bman654/clodex/blob/2f4c7f5fcb5c07a0fec81506111f428706413e50/src/provider-factory.ts#L821-L838)
- [SDK forceReasoning and provider options](https://github.com/bman654/clodex/blob/2f4c7f5fcb5c07a0fec81506111f428706413e50/src/provider-factory.ts#L1051-L1071)
- [Request effort extraction](https://github.com/bman654/clodex/blob/2f4c7f5fcb5c07a0fec81506111f428706413e50/src/sdk-adapter.ts#L154-L159)
- [Request/default precedence](https://github.com/bman654/clodex/blob/2f4c7f5fcb5c07a0fec81506111f428706413e50/src/sdk-adapter.ts#L665-L668)
- [Upstream wire test implementation](https://github.com/bman654/clodex/blob/2f4c7f5fcb5c07a0fec81506111f428706413e50/tests/openai-wire-effort.test.ts)

**Local test method:** extracted the relevant mapping functions/constants from the installed bundle, ran them in an isolated VM context, and passed resulting provider options through the installed OpenAI SDK's Responses serializer using a stubbed fetch. No credentials or real network calls were used. The test did not launch the CLI, exercise its patched UI, or run the upstream test suite.

**32 passing assertions:** four models × seven requested strings (none, low, medium, high, xhigh, max, Ultra) = 28 wire assertions; four request-extractor assertions = 4. Valid low through max values survived serialization for all four models. None survived for Luna/Terra/Sol and was omitted for Astra. Ultra was omitted for all. Only top-level output_config.effort was returned by the tested extractor; thinking budgets, disabled thinking, and per-message effort did not supply an effort value.

**Boundary:** this verifies mapping and serialization on the inspected OpenAI route. It does not verify live API acceptance, reasoning quality, OAuth transport, the running session's effective effort, or other provider routes. Source comments describe historical live tests, but those are not new live tests performed by this audit. Revalidate after integration changes.

## Source screening and exclusions

Approved scope: provider documentation and original independent/third-party benchmark results; CodeRabbit's own reports were subsequently authorized as **supporting** evidence. No Reddit, general commentary blogs, or unapproved commercial comparisons supply routing claims here.

- **FrontierMath:** excluded as independent superiority evidence under the user's sponsorship criterion. Epoch discloses OpenAI commissioning/funding and data access; this is a conflict-screening decision, not proof the scores are biased. [Disclosure](https://epoch.ai/latest/openai-and-frontiermath).
- **AA:** original comparison pages were used, with the transparency limitation in T1. No claim that commercial relationships have been exhaustively ruled out.
- **CodeRabbit:** authorized exception only. Vendor-controlled pipelines, mismatched snapshots, and incomplete configuration reporting must remain attached to the figures.
- **OpenAI announcement pages:** some full-page fetches returned HTTP 403. API model documentation was accessible. Unretrieved benchmark details were not filled in from secondary commentary.
- **Terminal-Bench original leaderboard:** [Harbor leaderboard](https://hub.harborframework.com/datasets/terminal-bench/terminal-bench/4?tab=leaderboard&leaderboard=4-0-0) returned a loading placeholder in the static fetch. The audit did not independently replicate AA's table from that leaderboard.
- **Removed as routing facts:** speculative retirement, undefined complexity ratings, generic over-engineering ratios, customer long-run anecdotes, universal writing/architecture winners, unsupported long-context quality cutoffs, blanket security refusals, and effort-to-runtime guarantees.

## Updating this evidence

For each retained numerical claim, record source/retrieval date, provenance, exact model/configuration, task/benchmark version, harness/pipeline, denominator, metric definition, and cost unit. Preserve missing fields explicitly. Do not update a number without its conditions. Prefer a task-relevant matched result over an aggregate, and describe a cost/quality tradeoff only when the data support both halves.
