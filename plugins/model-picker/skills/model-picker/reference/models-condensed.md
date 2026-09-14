# Model Selection Reference

Evidence snapshot: **2026-09-13**. Prices and benchmark pages can change. Scope is fixed to Haiku 4.5, Sonnet 5, Opus 5, Fable 5.1, GPT-5.6 Luna/Terra/Sol, and GPT-6 Astra; model identities were supplied by the user, not re-audited.

## How to use this reference

1. Identify the task in the shared taxonomy below. Gather quality requirements, latency tolerance, context size, tools, access/billing mode, and budget only where they affect the choice.
2. Apply documented constraints first, then compare **model + effort + harness** on relevant evidence. The same effort name does not imply the same compute across models.
3. Prefer task-specific evidence over aggregate scores. An adjacent benchmark supports a candidate, not an exact-task winner. Missing evidence means **unknown**, not unsuitable.
4. Separate quality, response-start latency, total completion time, token rates, cost per attempted task, and cost per solved task. Never substitute one for another.
5. If quality is unranked, give a provisional choice based on verified constraints; say that comparative quality is unestablished. Do not invent percentage advantages or certainty to fill the output format.
6. Read the linked evidence notes before using a numerical comparison. Recheck volatile claims if a date, price, access condition, or deployment version could change the decision.

**Evidence labels:** **P** = provider documentation/positioning; **E** = provider-run evaluation; **T** = third-party evaluation; **V** = commercial vendor's review experiment, supporting evidence only; **U** = no suitable comparative evidence established in this audit. Labels describe provenance, not a guarantee of impartiality. Source details and limitations are in [evidence.md](evidence.md).

## 1. Pricing and context constraints

Published standard API rates in **USD per million tokens**, not subscription costs or predicted task costs. Sources: [P1](evidence.md#p1-claude-pricing-and-retention), [P2](evidence.md#p2-openai-model-documentation).

| Model | Base input | Cache read | Output | Documented context capacity |
|---|---:|---:|---:|---|
| Haiku 4.5 | $1.00 | $0.10 | $5.00 | 200K |
| Luna 5.6 | $0.20 | $0.02 | $1.20 | 1.05M total; 922K max input, 128K max output |
| Terra 5.6 | $2.00 | $0.20 | $12.00 | 1.05M total; 922K max input, 128K max output |
| Sonnet 5 | $2.00 | $0.20 | $10.00 | 1M |
| Sol 5.6 | $4.00 | $0.40 | $20.00 | 1.05M total; 922K max input, 128K max output |
| Opus 5 | $5.00 | $0.50 | $25.00 | 1M |
| Astra 6 | $10.00 | $1.00 | $50.00 | 1.05M total; 922K max input, 128K max output |
| Fable 5.1 | $10.00 | $0.25 | $50.00 | 1M |

- **Cache writes are separate:** Claude 5-minute writes cost 1.25× base input; 1-hour writes cost 2×. Astra documentation lists $12.50/M cache writes. Do not assume every provider's cache policy is identical.
- **Long context:** the four GPT models charge 2× input and 1.5× output rates for the full request above 272K input tokens. Verify cache-specific charges for the route. Sonnet/Opus/Fable have no long-context token-rate surcharge. Batching is not a bypass for context limits or surcharges.
- **Batch:** Claude Batch API input/output rates are 50% lower; this is asynchronous API processing, not interactive Claude Code or Codex OAuth pricing.
- **Sol promotion:** current rates are available **at least through November 21, 2026**. Do not assert a guaranteed post-promotion price.
- **Tokenization:** newer Claude models use a newer tokenizer than Haiku 4.5; the pricing docs describe approximately 30% more tokens for the same text, varying with content. Equal token counts need not mean equal workloads across models.
- **Fable retention:** 30-day retention required; not available under ZDR unless expressly authorized by Anthropic. Treat this as an access constraint, not a quality judgment.
- **Opus fast mode:** $10/$50 base input/output; separate from effort. Availability and client support must be checked.
- **Subscription access:** these API rates do not establish marginal cost, quota consumption, or limits through ChatGPT/Codex OAuth or Claude subscriptions.

**Valid rate comparisons, not task-cost claims:** Opus's standard input/cache-read/output rates are each 25% above Sol's. Opus has half Fable's base input/output rates but **twice its cache-read rate**. Terra has half Sol's input rate but 60% of its output rate. Sonnet and Terra share input/cache-read rates; Sonnet has a lower output rate. Luna has lower rates than Haiku in all three listed categories.

## 2. Effort and execution settings

Sources: [P2](evidence.md#p2-openai-model-documentation), [P3](evidence.md#p3-claude-effort-and-task-positioning), [I1](evidence.md#i1-clodex-effort-verification).

| Model | Supported control | Documented default / interpretation |
|---|---|---|
| Haiku 4.5 | Thinking disabled or manual extended-thinking budget | Do not assign the newer Claude `output_config.effort` scale; do not invent a budget-to-quality mapping. |
| Luna / Terra / Sol 5.6 | `none`, `low`, `medium`, `high`, `xhigh`, `max` | API default `medium`; `none` does not imply determinism or zero cost. |
| Sonnet 5 | `low`, `medium`, `high`, `xhigh`, `max`; thinking is a separate control | Default `high`, adaptive thinking by default. Thinking disabled **still permits tools**. |
| Opus 5 | `low`, `medium`, `high`, `xhigh`, `max` | API default `high`; thinking cannot be disabled at `xhigh`/`max`. |
| Fable 5.1 | `low`, `medium`, `high`, `xhigh`, `max` | Default `high`; thinking always on. |
| Astra 6 | `low`, `medium`, `high`, `xhigh`, `max` | No `none`; clodex declares `medium` as its OpenAI default. Do not confuse client and API defaults. |

**Selection guidance:** Claude's effort documentation starts Opus/Fable at `high` and advises measured step-downs; its cost-optimization evaluation supports testing `low` for some workloads. These optimize different objectives. Use task-specific results below where available. Otherwise identify an effort choice as a starting configuration, not a measured optimum. Higher effort is not a correctness guarantee; escalation should follow observed quality failures, not a universal time threshold. Effort changes can also affect caching; verify the client's supported mechanism.

### GPT effort through clodex

Installed **clodex 2.11.6** was inspected on 2026-09-13. **32 offline assertions passed** using its installed mapping functions and installed OpenAI SDK request serialization; no live API/OAuth/session test was performed. [I1](evidence.md#i1-clodex-effort-verification)

- On the inspected OpenAI route, `low`/`medium`/`high`/`xhigh`/`max` are sent unchanged for all four GPT models; `none` is sent for Luna/Terra/Sol, omitted for Astra.
- The extractor reads top-level `output_config.effort`; translation falls back to a supplied default when absent. The inspected OpenAI capability default is `medium`.
- That extractor does not derive effort from `thinking.budget_tokens`, `thinking.type: disabled`, or per-message `output_config` entries.
- The installed `forceReasoning: true` fix prevents the SDK's older model-name recognition from dropping Astra's valid effort.
- **`Ultra` is not a supported effort setting.** It was omitted by the tested mapping. Any multi-agent product mode is a separate harness feature, not a model effort.
- These findings do not prove live backend behavior or cover every provider route. Recheck if clodex, the SDK, routing, or Claude Code's request format changes.

## 3. Comparable measurements

### Repository issue-solving: provider evaluation E1

Anthropic's **SWE-bench Pro**, cost per **solved** task, with source conditions in [E1](evidence.md#e1-anthropic-cost-and-intelligence-evaluations). This is provider-run evidence, not an independently reproduced universal coding ranking.

| Model/configuration | Pass rate | USD per solved task |
|---|---:|---:|
| Sonnet 5 default | 77.4% | $0.84 |
| Opus 5 low | 84.0% | $0.25 |
| Fable 5.1 low | 88.6% | $0.54 |
| Opus 5 default | 91.7% | $1.01 |
| Fable 5.1 default | 92.1% | $1.19 |

Opus low exceeds Sonnet default by **6.6 percentage points**, at approximately **70% lower cost per solved task in this evaluation**. Fable low exceeds Opus low by **4.6 points**, at **2.16×** the cost per solved task. Default Opus/Fable pass rates are described as within noise; do not declare Fable the winner from 0.4 points.

### Cross-provider task evidence T1

Artificial Analysis **Intelligence Index v4.3** snapshot; all rows at **max effort**, Claude with adaptive reasoning, Fable with **Default Fallback**. [T1](evidence.md#t1-artificial-analysis-v43)

| Model | Terminal-Bench 4.0 | SciCode | AA-LCR v1.1 | GDPval-AA v2 rating | AA weighted USD/task |
|---|---:|---:|---:|---:|---:|
| Luna 5.6 | 12% | 54% | 84% | 1489 | $0.18 |
| Terra 5.6 | 35% | 55% | 83% | 1477 | $1.40 |
| Sol 5.6 | 40% | 57% | 84% | 1624 | $1.99 |
| Sonnet 5 | 14% | 54% | 82% | 1501 | $5.09 |
| Opus 5 | 49% | 56% | 79% | 1735 | $5.86 |
| Fable 5.1 | 52% | 63% | 85% | 1764 | $7.63 |
| Astra 6 | 59% | 56% | 81% | 1580 | $3.26 |

- **Scope:** Terminal-Bench tests terminal agents; SciCode tests scientific coding; GDPval-AA tests professional work. None is a direct measure of every coding, writing, or business subtask.
- **Costs:** weighted averages across the Index's ten evaluations, including reasoning and cache accounting. They are neither coding-specific nor cost per successful task. Do not pair them with Terminal-Bench pass rates to calculate coding cost per success.
- **Context:** AA-LCR tests approximately **10K–100K tokens**, not 512K–1M. No extreme-context winner follows from it.
- **Precision of claims:** ratings are not percentages; small differences may be noise. These max-effort results do not establish rankings at low/medium/high.
- Haiku is omitted from this matched configuration table rather than mixing its non-reasoning result into it. This is not evidence that Haiku cannot perform these tasks.
- Aggregate Index scores are intentionally not used as a universal task ranking or a made-up complexity scale.

**Tradeoffs supported here:** Astra has the highest observed terminal score among these rows, while Fable has the highest observed SciCode and professional-work scores. Opus and Sol overlap in coding: Opus's terminal score is higher; their SciCode scores are close, and Sol has lower standard token rates. Luna/Sonnet have several close task results but very different aggregate costs. Terra max improves substantially over Luna max on hard terminal tasks, not on every task family.

### Research and response-start latency

**E1, DeepResearch Bench II:** Sonnet default 56% at $1.20/task; Opus default 71% at $6.71/task; Fable low 66% at $4.66/task; Fable default 65% at $7.12/task. These establish Claude research overlap and a measured cost/score tradeoff, not superiority over GPT models absent from this experiment.

**T2, Luna max versus Terra medium:** Index v4.3 scores 38 versus 30, both $0.18 weighted cost/task; measured time to first token **121.85s versus 1.82s**. This is a quality/response-start tradeoff, not a universal latency constant or evidence that one is better at all interactive coding. [T2](evidence.md#t2-effort-and-latency-comparison)

## 4. Code review: CodeRabbit supporting evidence only

**Do not read this table as one leaderboard.** Different datasets, denominators, prompts, effort/profile combinations, pipeline stages, and snapshots prevent clean model-only comparisons. Precision refers to the evaluated comment stream, not general model accuracy. Sources and definitions: [V1–V4](evidence.md#v1-coderabbit-sol-and-terra).

| Model/configuration | Reported known-issue coverage | Reported comment precision | Conditions / limitation |
|---|---:|---:|---|
| Sol 5.6 | 69/99 = 69.7% actionable pass | 31.6% | V1; 231 comments, 61 nitpicks; exact effort not established in audit. |
| Terra 5.6 | 53/101 = 52.5% actionable pass | 35.7% | V1; 143 comments, 21 nitpicks; denominator differs from Sol. |
| Sonnet 5 | Approximately 50–51% bug catch | Approximately 38–40% | V2; ranges across reported configurations, not one exact paired point. |
| Opus 5 senior-reviewer, x-high | 55.2% actionable pass | 39.3% actionable precision | V3; three runs/configuration averaged; post-pipeline results. |
| Fable 5.1, “Low” reasoning | 64/105 = 61.0% recall | 37.3% | V4; 45 tasks, 166 final comments, 18:38 mean latency/task. |
| Fable 5.1, “High” reasoning | 57.1% recall | 36.4% | V4; same 45 tasks, 165 final comments, 21:36 mean latency/task. |

No verified CodeRabbit figures are included for **Haiku, Luna, or Astra**. Do not transfer Fable 5's results to Fable 5.1. “Low”/“High” above are the experiment's labels; do not assume they map to API effort or your review harness without checking.

**Permitted use:** identify configurations worth testing for coverage versus actionable-comment quality. Sol's report suggests a coverage/noise tradeoff; Opus/Sonnet reports motivate precision-oriented testing, not a proven cross-model ranking. Fable's within-study result shows higher reasoning did not improve the reported metrics in that test. No complete review-cost comparison or universal winning reviewer is established. Do not recommend Sol low/medium using an experiment whose effort is unspecified. Anthropic also documents Sonnet's sensitivity to conservative review prompts [P3](evidence.md#p3-claude-effort-and-task-positioning).

## 5. Shared task taxonomy

Use these exact categories for every model. **Every model is in scope for comparison in every row; an omitted candidate has U evidence here, not a demonstrated inability.** Candidate sets below reflect available evidence, not exhaustive capability lists. Broad benchmark coverage does not prove superiority on every named subtask.

| Task family and common use cases | Comparative basis / limits |
|---|---|
| **Classification/extraction:** routing, tagging, triage, entities, JSON/schema extraction, document fields | P positions Haiku/Luna for volume work and Sonnet for structured pipelines. Luna's token rates are lower than Haiku's; comparative task quality U. |
| **Text transformations:** summaries, rewriting, editing, translation, localization, formatting | U for an eight-model task ranking; use verified costs, latency constraints, and output checks, not an invented writing winner. |
| **Interactive assistance:** chat, tutoring, explanations, brainstorming, quick Q&A | Haiku P positioning and T2 illustrate responsiveness considerations. No universal fastest/best model established at matched settings. |
| **Code understanding/search:** navigation, symbol lookup, dependencies, explanations, documentation | U for a direct search ranking. Issue-solving is adjacent evidence, not proof that Haiku or any other model is the best search worker. |
| **Bounded coding:** small fixes, scripts, functions, boilerplate, API integration | Luna/Terra/Sol/Sonnet/Opus/Fable/Astra overlap in T1 coding evidence; E1 supports testing Opus/Fable low. No universal routine-coding default follows. |
| **Repository implementation:** multi-file features, migrations, refactors, upgrades | E1 directly informs issue-solving; T1 informs terminal agents. Compare Opus/Fable/Sol/Astra and budget alternatives; exact subtask rankings U. |
| **Debugging:** reproduction, root cause, regression fixes, performance/concurrency diagnosis | Overlaps coding for all candidates above. Do not assign “bug hunts” to Sol and “debugging” to Fable as if different measured specialties. |
| **Testing:** unit/integration tests, test repair, coverage gaps, edge cases | Coding evidence is adjacent; dedicated testing superiority U. |
| **Code review:** discovery, severity ranking, false-positive filtering, security review | V1–V4 cover Sol/Terra/Sonnet/Opus/Fable with incompatible snapshots. Measure precision and coverage separately; no definitive winner. |
| **Architecture/planning:** design alternatives, decomposition, migration plans, specifications | Exact comparative evidence U. Do not present a frontier-model preference as a measured architecture lead. |
| **Terminal/operations:** CLI workflows, builds, CI/CD diagnosis, environment repair, DevOps/SRE | T1: Astra/Fable/Opus/Sol/Terra/Luna/Sonnet comparisons at max. Terminal success is not a direct ranking of every SRE subtask. |
| **Browser/desktop:** navigation, forms, GUI targeting, screenshots, multi-app workflows | P supports Sonnet/Opus/Astra use cases; a matched cross-provider winner is not established here. Keep OSWorld versions and visual targeting separate. |
| **Document reasoning:** Q&A, cross-document synthesis, grounded answers, evidence reconciliation | T1 AA-LCR compares seven models over 10K–100K; Fable/Sol/Luna/Terra/Sonnet/Astra/Opus all overlap. |
| **Extreme context:** retrieval and reasoning over 256K–1M inputs | P capacity/pricing only. Quality ranking U; no hard Luna-256K or Sol-500K reliability cutoff established. |
| **Research:** web/source discovery, factual verification, literature/market synthesis | E1 compares Sonnet/Opus/Fable on DeepResearch Bench II. Sol/Astra provider positioning is not a matched victory over them. |
| **Writing/deliverables:** email, short-form copy, long-form prose, reports, presentations | T1 professional-work evidence overlaps seven models; individual formats, aesthetics, and style rankings U. |
| **Business/data:** spreadsheets, financial analysis, cleaning, SQL, statistics, charts | T1 professional work and SciCode are partial evidence; do not infer financial correctness or a winner for every subtask. |
| **Math/science:** routine math, advanced proofs, scientific code, simulations, research workflows | T1 SciCode supports scientific-coding comparisons. Frontier-math ranking U under this audit's source restrictions. |
| **Visual understanding:** OCR, tables, charts, diagrams, screenshot interpretation | Separate from text Q&A and GUI action success; a complete matched ranking U. |
| **Security:** threat models, secure review, vulnerability discovery, authorized exploit research | Separate capability, authorized task, tools, safeguards, and access. A failed exploit test does not imply refusal of all defensive work. No blanket provider exclusion. |
| **Orchestration/autonomy:** bounded workers, lead agents, parallel research, dependent chains, long runs | E1 has specific delegation experiments, not a universal lead/worker winner. Test a single model at lower effort before assuming delegation saves cost. |

## 6. Per-model distinctions using the shared tasks

These summaries reference the measurements above rather than inventing non-overlapping specialties.

| Model (API ID) | Where the evidence distinguishes it | Competitive overlap and limitation |
|---|---|---|
| **Haiku 4.5** (`claude-haiku-4-5-20251001`) | P: checkable classification/extraction and responsive interaction; 200K limit. | Compare Luna on volume rates and actual quality/latency. No verified claim of cheapest overall, best code search, or impending retirement. |
| **Luna 5.6** (`gpt-5.6-luna`) | T1: scientific coding, document reasoning, professional work overlap Sonnet at max with lower aggregate cost. Lowest listed token rates. | Terra max improves hard-terminal score; Terra medium starts responding sooner than Luna max in T2. Do not extrapolate max quality to none/low. |
| **Terra 5.6** (`gpt-5.6-terra`) | T1: higher hard-terminal score than Luna max, lower than Sol max; T2: responsive medium configuration. | Scientific coding/document reasoning are close to Luna/Sol in T1. “Everyday coding winner” U; Sonnet shares input/cache rates and has lower output rates. |
| **Sonnet 5** (`claude-sonnet-5`) | P: coding, structured extraction, browser/computer use; E1: lower research cost with lower score than Opus/Fable. | Compare Luna for volume work; Opus/Fable low for repository issue-solving. V review precision/coverage depends on prompt and pipeline; no blanket avoid-review rule. |
| **Sol 5.6** (`gpt-5.6-sol`) | T1: coding/terminal/professional work at lower standard rates than Opus; V1 motivates review coverage testing. | Opus has higher observed terminal/professional scores at max; scientific coding close. No exclusive research/slides specialty or verified “avoid whole-repo fixes” rule. |
| **Opus 5** (`claude-opus-5`) | E1: low-effort repository issue-solving value; T1: stronger terminal score than Sol max; research/professional-work overlap. | Fable low trades higher E1 pass rate for higher solved-task cost. Fable cache reads are cheaper. V3 is precision-oriented supporting evidence only. |
| **Astra 6** (`gpt-6-astra`) | T1: highest observed hard-terminal score among the seven max configurations; P: computer use. | Fable leads retrieved scientific-coding/professional-work scores. No universal math, context, or budget-unlimited winner. |
| **Fable 5.1** (`claude-fable-5-1`) | E1: demanding repository work and useful low configuration; T1: highest observed SciCode/professional-work scores; inexpensive cache reads. | Opus competes on issue-solving cost; Astra leads T1 terminal score. V4 low/high review results are within-study, not a universal reviewer ranking. |

## 7. Recommendation guardrails

- For **repository issue-solving under API cost constraints**, Opus low and Fable low are evidence-backed candidates; explain E1's score/cost tradeoff, not a general coding percentage.
- For **hard terminal work**, use T1 to discuss max-effort alternatives. A lower-effort recommendation is provisional unless separately measured.
- For **research**, E1 supports a Sonnet cost versus Opus/Fable score tradeoff. It does not rank the absent GPT models.
- For **code review**, CodeRabbit is supporting evidence only. Ask whether coverage or actionable-comment quality matters when this changes the choice; do not calculate cross-snapshot superiority.
- For **unranked tasks**, choose using verified constraints and clearly state the evidence gap. Do not invent a quality penalty for a lower-priced model.
- Preserve uncertainty: vendor statements, third-party measurements, and local integration checks answer different questions. No score guarantees correctness, safe deployment, or success on the user's task.

## Maintenance

Update the snapshot date and source notes together. Record benchmark version, model configuration, harness/pipeline, cost unit, dataset/denominator, uncertainty, and access conditions. Never mix snapshots silently. Retire unsupported claims rather than filling gaps with anecdotes. Keep provider-sponsored research out of the independent-evidence category; CodeRabbit is the specifically approved supporting-source exception. See [source screening and exclusions](evidence.md#source-screening-and-exclusions).
