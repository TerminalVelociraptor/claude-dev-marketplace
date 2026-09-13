# AI Model Selection Reference

## Quick Picker

| Model | Complexity | Price (in/out per 1M) | Context | Pick for |
|---|---:|---:|---:|---|
| **Claude Haiku 4.5** | 4/10 | $1 / $5 | 200K | Fast, cheap routing/extraction/chat; exploration subagents |
| **GPT-5.6 Luna** | 5/10 | $0.20 / $1.20 | 1.05M usable to ~256K | Cheapest high-volume work; bounded coding at xhigh/max |
| **GPT-5.6 Terra** | 6/10 | $2 / $12 | 1.05M | Default everyday coding/terminal at low/medium effort |
| **Claude Sonnet 5** | 7/10 | $2 / $10 | 1M flat | Knowledge work, browser/computer use at volume; parallel workers |
| **GPT-5.6 Sol** | 8/10 | $4 / $20 (promo to Nov 21; list $5/$30) | 1.05M | Terminal agents, bug hunts, web research, slides, recall work |
| **Claude Opus 5** | 8/10 | $5 / $25 | 1M flat | Complex agentic coding, debugging, enterprise work |
| **GPT-6 Astra** | 9/10 | $10 / $50 | 1.05M | Computer use, security research, frontier math, 512K–1M recall |
| **Claude Fable 5.1** | 9/10 | $10 / $50 | 1M flat | Multi-hour autonomous coding, polished deliverables, architecture |

**Pricing caveats:**
- All OpenAI models incur 2x input / 1.5x output surcharge above 272K tokens (applies to whole request).
- Claude pricing stays flat to 1M. Sonnet 5's tokenizer produces 1.0–1.35x more tokens than older Claude models.

## Decision Rules (from research)

- **Bigger model at low effort often beats smaller at high effort** on both quality and cost per task (e.g., Opus 5 low beats Sonnet 5 default effort on SWE-bench Pro: 84% vs 77.4%, $0.25 vs $0.84 per task).
- **Diminishing returns above medium/high effort:** xhigh→max adds ~1 index point, 2–5 min latency. Start medium/high; raise effort only if tests fail.
- **On long agent loops, cheaper models cost more per success.** Terra 40.7% pass / 55K tokens vs Sol 63.7% / 21K—Sol ends cheaper per solved task.
- **Orchestrator + workers proven pattern:** Fable lead + 25 Sonnet workers ≈50% cheaper, 7x faster, 10–12 points lower quality. Sol→Luna, Opus→Haiku all work.
- **Over-engineering common at top end** (Sol, Opus, Fable). Use explicit scope rules in prompts.
- **Claude refuses exploit development.** For defensive security: use Astra or Sol. Anthropic directs cyber work to Opus 5 over Sonnet 5.

## Per-Model Guide

### 1. Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
Fast, cheap (half price via Batch). 200K context (no 1M like others). 77–95 tokens/s. Knowledge cutoff Feb 2025. Possible retirement ~Oct 2026.
- **Use:** High-volume checkable work (classification, extraction, triage), latency-critical chat, read-only subagents, Opus 5 worker.
- **Thinking setting:** Off (default) for most traffic; low budget (~1–4K) for short reasoning; high budget (~16–32K) for bounded reasoning on long documents.
- **Avoid:** Long coding loops (fell far behind), >200K context, accuracy-critical reasoning (GPQA 63% vs Opus 92%), unsupervised test-driven coding.

### 2. GPT-5.6 Luna (`gpt-5.6-luna`)
80% price cut July 2026. Retrieval collapses above ~256K (MRCR 41% vs Terra 90%). 105–120 tokens/s. Effort: none/low/medium (default)/high/xhigh/max.
- **Use:** Bounded coding (DeepSWE 67% at $0.61), terminal work (Terminal-Bench 84.7%), worker under Sol; high-volume pipelines.
- **By effort:** none=deterministic; low=fast drafts; medium=baseline; high=harder logic; xhigh=Codex standard; max=hardest tightly-specified.
- **Avoid:** Context >256K, ambiguous work, multi-step procedures, hard computer use/frontier tasks, acting as orchestrator.

### 3. GPT-5.6 Terra (`gpt-5.6-terra`)
Strong recall to ~512K (MRCR 89.6%). 89 tokens/s at medium, 162s first token at max. Effort: none/low/medium (default)/high/xhigh/max (none only with function tools on Chat).
- **Use:** Value on scoped coding (Terminal-Bench 87.4%, SWE-Bench 63.4%, within 2–3 points of Sol at half price), long documents, fast interactive work, implementation worker.
- **By effort:** none=routing over large docs; low=drafting/transforms; medium=scoped agent work; high=dependent steps/debugging; xhigh=long background work (compare cost vs Sol).
- **Avoid:** Long autonomous runs (Sol cheaper per success), code review (52.5% vs Sol 69.7%), computer use, >272K tokens without batching.

### 4. Claude Sonnet 5 (`claude-sonnet-5`)
Flat 1M pricing. 57–60 tokens/s. Jan 2026 cutoff. Effort: thinking disabled / low / medium / high (default) / xhigh / max. Eligible for zero data retention.
- **Use:** Knowledge work/dollar (GDPval 1618 ≈ Opus 4.8), terminal/agentic coding with clear spec, browser/computer use at volume (OSWorld 81.2%), predictable pipelines.
- **By effort:** Disabled=lowest latency, no tools; low=short scoped work; medium=matches Sonnet 4.6 at high; high=everyday complex; xhigh=hardest (check Opus 5 low first); max=rarely worth it.
- **Avoid:** Hard coding when cost/task matters (Opus 5 low cheaper), ambiguous work, security (0% exploit dev by design), code review (50% vs Sonnet 4.6 63%), high-volume simple work.

### 5. GPT-5.6 Sol (`gpt-5.6-sol`)
55–75 tokens/s. Promo until Nov 21. Effort: none/low/medium (default)/high/xhigh/max/**Ultra** (4 parallel agents, ~3x cost, +3 points).
- **Use:** Terminal/CLI agents (Terminal-Bench 88.8%, 91.9% Ultra), long multi-step work, broad bug audits (caught 69.7% in CodeRabbit, but 32% accurate), web research, slides.
- **By effort:** none=tone without cost; low=well-defined tasks; medium=normal coding; high=multi-step debugging; xhigh=high-stakes reasoning (auth/threat models); max=hardest analysis; Ultra=long agent runs.
- **Avoid:** Maximum capability when budget allows (Astra wins), whole-repo fixes (SWE-bench 64.6%), novel problems, GUI clicking, over-engineers (code 3x larger than Fable), >500K-token retrieval.

### 6. Claude Opus 5 (`claude-opus-5`)
50–53 tokens/s at all efforts; 58s first token at max. May 2026 cutoff. Effort: low / medium / high (default) / xhigh / max. Fast mode (2.5x speed, waitlist, $10/$50).
- **Use:** Best frontier agentic coding value (CursorBench 70% at $8.23 vs Fable 70.5% at $17.32), novel problem-solving (ARC-AGI 30.2% vs Sol 7.8%), long-context work (flat 1M, 3.8x cheaper than Astra on 500K).
- **By effort:** low=subagents ($1.10/task, Index 40); medium=agentic balance ($2.19); high=complex reasoning ($3.61); xhigh=30+ min runs ($4.88); max=correctness-critical ($5.86, if max fails try Fable).
- **Avoid:** Hardest science (Terminal-Bench-Science 29% vs Fable 52.6%), frontier math, simple high-volume work, sole reviewer (55% catch vs Sol 70%), loosely scoped tasks, offensive security (blocked).

### 7. GPT-6 Astra (`gpt-6-astra`)
50–62 tokens/s. Critical cyber capability (gated Daybreak program). Effort: low/medium/high/xhigh/max (no `none`). April 2026 cutoff. Released Sept 3, 2026.
- **Use:** Computer/browser use (OSWorld 72.6%, ScreenSpot 92.7%), long terminal work (Terminal-Bench 4.0: 57.7% vs Fable 55.8%), defensive security (ExploitBench 100%, SRE-Bench 88%), frontier math (FrontierMath T4: 97.6%).
- **By effort:** low=simple if needing Astra (Index 46); medium=recommended start (general analysis, multi-step changes); high=20+ min runs; xhigh=measurable failures at high; max=hardest one-offs (no gain over xhigh).
- **Avoid:** General coding (tied/behind Fable/Opus), expert reasoning (Last Exam 57.2% vs Fable 65%), everyday work (Sonnet matched it cheaper/faster), latency-sensitive at high+, >272K caching loops, low friction (safety halts, legalistic, ChatGPT limits).

### 8. Claude Fable 5.1 (`claude-fable-5-1`)
52 tokens/s at medium, 268s first token at max. Thinking always on. June 2026 cutoff. Requires 30-day retention (no zero-retention option). Effort: low/medium/high (default)/xhigh/max.
- **Use:** Long autonomous agentic coding (CursorBench 73.4% highest, customer 38-hour runs), agentic science (Terminal-Bench-Science 52.6%), business deliverables (GDPval 1853, highest), debugging/root-cause, code review (balanced).
- **By effort:** low=high quality bounded cost (Anthropic says often beats Opus/Sonnet per task); medium=routine work (≈Fable 5 full, beats Opus high on score/speed/cost); high=demanding multistep; xhigh=30+ min runs (may spawn unneeded subagents); max=hardest problems ($3.76+/task).
- **Avoid:** Everyday work (Opus half price, Anthropic's default), latency-sensitive/high-volume, frontier math/computer use/security (Astra stronger, Fable filters refuse), short-form writing (Sol better), saying "I don't know" (attempted 73% of wrong answers), over-reaches scope.

## Quick Task → Model Picker

| Task | Pick | Alternatives |
|---|---|---|
| Classification/routing/extraction at volume | Luna none/low | Haiku (if Claude-only) |
| Live chat, low latency | Haiku off | Luna low, Sonnet low |
| Codebase search subagents | Haiku | Sonnet/Opus low |
| Q&A over docs >256K tokens | Opus/Sonnet (flat 1M) | Astra (best recall at 512K–1M, but surcharge) |
| Routine, well-scoped coding | Terra medium | Sonnet high, Opus low, Luna xhigh |
| Code review, most bugs (noisy) | Sol low/medium | Fable high |
| Multi-file features/refactors | Opus high | Fable medium/high |
| Hard debugging | Fable high | Opus high/xhigh |
| Terminal/DevOps agents | Sol medium/high | Astra high, Terra medium |
| Computer/browser automation | Astra high | Sonnet high (volume), Opus xhigh |
| Multi-hour autonomous runs | Fable xhigh | Opus xhigh, Astra high |
| Architecture/planning | Fable high | Opus high |
| Reports/spreadsheets/finance | Fable medium/high | Sonnet high (budget) |
| Defensive security | Astra xhigh/max | Sol xhigh, Terra (budget) |
| Frontier math/science | Astra/Fable max | — |

## Intelligence Index (Artificial Analysis, current version)
Astra 53, Fable 5.1 53, Opus 5 51, Sol 47, Terra 42, Luna 38, Sonnet 5 38, Haiku 4.5 18.
*Note: Rescaled multiple times; only compare within the same version.*

## Data Notes
- OpenAI benchmark data mostly third-party (OpenAI blocked automated fetching).
- Artificial Analysis index varies by version; treat as rough ranking.
- Benchmark versions matter (Terminal-Bench 2.1 vs 4.0 rank models differently).
- Prices change often; verify vendor pages before committing.
