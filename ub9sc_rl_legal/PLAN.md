# Plan: an RL environment and a legal formal-methods benchmark on reglab/spec

Written Oct 30, 2026 by ub9sc (ultimate brando9 scalable coworker, Brando Miranda's assistant). Side project, vb-priv and the other four priorities keep the hardware.
Route (Brando, Oct 29): cheap only, Allen's Gemini preview key, no GPUs, no open-weight models. The key is read in-process from a file and never stored in the repo.

## Principle
Velocity first: the cheapest test that answers "should this exist?" before anything big.

## Idea 1: RL environment of the repo's 250 cases (natural language)
- `spec_env/`: one-step Gym-style env (`reset(i)`, `step(text)`), fixed scorer (exact label, the repo's substring rule counts "Not Eligible" as a hit for "Eligible"), zero-shot Gemini baseline.
- Reward: 1 if the parsed label equals gold. Always report complete-case and inconclusive-case accuracy side by side (the paper's tradeoff).
- Next: statute-only retrieval corpus (C.R.S. Title 8, public); variants by withholding facts from the 110 complete cases; splits by case family; reward shaping for the missing-fact list.

## Idea 2: formal-methods version
- Facts of a case are a partial assignment (true / false / unknown). A provision is a Lean rule on complete facts. The verdict is derived, not predicted: ELIGIBLE if every completion of the unknowns satisfies the rule, NOT ELIGIBLE if none does, INCONCLUSIVE otherwise. A kernel checks it (`decide`), no judge.
- `legal_fm/`: 4 provisions, 20 dataset-grounded tests, two task types: formalize (card to Lean rule, scored by the kernel on hidden tests) and extract (case text to facts, verdict derived).
- Next: provisions with exceptions, thresholds and date arithmetic; task (c) minimal missing-fact set with a certificate; human legal check of every fact label.

## De-risking order
1. Test 0 (done): does the baseline presumptuousness show up with a cheap model and no guides? See README.
2. Test 2 (done, small): can a frontier model formalize bright-line provisions into Lean? See README.
3. Test 1: does an RL / best-of-n loop move inconclusive accuracy without hurting complete accuracy? Not run; needs the open-weight route Brando has parked.

## Cost
Gemini preview key (Allen's), tokens only, see README. No money from Brando. No GPUs.
