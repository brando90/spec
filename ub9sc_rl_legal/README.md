# RL environment and legal formal-methods benchmark on reglab/spec (feasibility check)

Started Oct 30, 2026 by ub9sc (ultimate brando9 scalable coworker, Brando Miranda's assistant). Plan: [PLAN.md](PLAN.md). Everything here is a first feasibility check, not a finished benchmark.
Route: Allen's Gemini preview key only (read from a file on the snap cluster, never stored here), no GPUs, no open-weight models. Generation ran on skampere1 and skampere2 (CPU), Lean checking ran locally (Lean 4, no Mathlib).
The upstream repo has no LICENSE file; check before redistributing `spec_env/cases.json` (the repo's own 250 cases as JSON).

## Idea 1: RL environment over the 250 cases (`spec_env/`)
- `env.py`: one-step Gym-style env, `reset(i)` gives the case prompt, `step(text)` gives reward 1 if the parsed label equals gold, plus an `info['presumptuous']` flag.
- `scorer.py`: exact label match. The repo's `run_benchmark.py` uses a substring test, so "Eligible" matches inside "Not Eligible".
- Test 0: zero-shot `gemini-3-flash-preview`, no statutes, no retrieval, prompt tells it to answer INCONCLUSIVE when a needed fact is missing. All 250 cases scored.

| metric | result |
|---|---|
| overall | 200/250 (0.800) |
| complete cases (110) | 73/110 (0.664) |
| inconclusive cases (140) | 127/140 (0.907) |
| decisive answer on an inconclusive case | 13/140 (0.093) |
| repo's substring rule, overall | 206/250 (0.824), 6 hits too many |
| tokens (input / output incl. thinking) | 52,890 / 738,732 |

- With an explicit abstain instruction the model is not presumptuous (the paper's ~15% on inconclusive cases is for standard RAG prompts without one); it over-abstains instead: 34 of the 110 complete cases got INCONCLUSIVE.
- So the tradeoff the paper describes is there, flipped: the reward has headroom on complete cases (0.664) at the cost of inconclusive accuracy. That is the signal an RL loop would train on.
- Not tested: the unprompted baseline (no abstain instruction), retrieval over public statutes, any training. Test 1 (RL or best-of-n moves both numbers) is not run: it needs a trainable model, and Brando parked GPUs and open-weight models.
- Rerun: `python3 -m spec_env.run_baseline --model gemini-3-flash-preview --key KEYFILE --out out.jsonl`, then `python3 -m spec_env.summarize out.jsonl`. Raw rows in `results/`.

## Idea 2: formal-methods version (`legal_fm/`)
- A case is a partial assignment of facts (true / false / unknown). A provision is a Lean rule on complete facts. The verdict is derived, not predicted: ELIGIBLE if every completion of the unknowns satisfies the rule, NOT ELIGIBLE if none does, INCONCLUSIVE otherwise (outcome invariance). The Lean kernel checks it with `decide`.
- `provisions.json`: 4 provisions (seasonal worker, public-health-emergency quit, construction quit, substance-use-disorder discharge) with 20 tests, each tied to a numbered case of the repo. Provision cards are my paraphrases from the repo's gold explanations, not statute text, and every fact label is mine: a human legal check is still needed.
- `gen_lean.py` writes the Lean files; `ref/*.lean` are the reference rules, all 20 tests pass in the kernel.
- Two task types: formalize (provision card to a Lean `rule`, scored by the kernel on hidden tests) and extract (case text to fact values, verdict derived).

| model | formalize: all tests pass | extract: verdict correct | extract: facts exact |
|---|---|---|---|
| gemini-3-flash-preview | 12/12 samples | 16/20 | 15/20 |
| gemini-3.1-pro-preview | 8/8 samples | 15/20 | 14/20 |

- Tokens (input / output incl. thinking): flash 12,676 / 52,379; pro 10,600 / 15,285.
- Formalization is saturated on these provisions: every sample compiled and passed every hidden test. They are conjunctions with one negation and one disjunction, too easy to tell models apart. The first benchmark needs exceptions, thresholds and date arithmetic.
- The difficulty sits in extraction and abstention: the misses are cases 99-101 (seasonal regain clause), 102 and SUD case 4. Several are label disputes, not model errors: case 4 states a program start date but no medical-statement date, so the model's "unknown" is defensible while the repo's gold says Eligible; cases 3 and 5 both say "separation was not violational" but gold counts it as present in 3 and missing in 5. These are the places a human legal check must settle.
- Rerun: generate on a host with the key, `python3 -m legal_fm.gen_formal --model M --key KEYFILE --out gens.jsonl`, then check locally with `python3 -m legal_fm.check_formal gens.jsonl` (needs `lean` on PATH).

## Could it extend VeriBench?
- Yes as a new domain: legal rules as verified specs, with the Lean kernel as the checker and no judge. The abstain-when-a-premise-is-missing property is a theorem here, which also fits the cert-judge line.
- Not yet: the 4 provisions are trivially formalizable, so they cannot rank models. It would need the harder provisions above first.

## Open questions
- Should the first real benchmark be hard provisions with a human legal check, or stay a model-vs-kernel comparison with no legal claims?
- Which models, if GPUs and open-weight models come back (Test 1)?
- Cost: only Allen's preview key tokens (about 0.8M tokens per full Idea 1 run); no money, no GPU hours.
