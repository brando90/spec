"""Idea 2, phase 1 (needs the Gemini key, run where it lives): model generations for two task types.
  formalize: provision card -> Lean `rule` body.   extract: case text -> {field: true/false/null}.
Usage (from ub9sc_rl_legal/): python3 -m legal_fm.gen_formal --model M --key KEYFILE --out gens.jsonl [--samples 3]
"""
import argparse, json, pathlib, concurrent.futures as cf
from spec_env import gemini
from .gen_lean import interface

HERE = pathlib.Path(__file__).parent
SYS_F = ("You formalize legal provisions into Lean 4 (no Mathlib). You are given a provision in plain English and a Lean "
         "prelude. Reply with ONLY the Lean definition `def rule (f : F) : Bool := ...` (one definition, no imports, no "
         "markdown fences, no extra text). `rule f` is true exactly when the claimant gets a full award on complete facts f.")
SYS_E = ("You extract facts from a case for a legal provision. For each field answer true if the case states or clearly "
         "implies it, false if the case states or clearly implies the opposite, null if the case does not say. Do not "
         "assume missing facts. Reply with ONLY a JSON object mapping each field name to true, false or null.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--key", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--samples", type=int, default=3); ap.add_argument("--conc", type=int, default=4)
    ap.add_argument("--no-extract", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(HERE / "provisions.json"))["provisions"]
    cases = {c["no"]: c for c in json.load(open(HERE.parent / "spec_env" / "cases.json"))}
    jobs = []
    for p in spec:
        for s in range(a.samples):
            jobs.append(dict(kind="formalize", prov=p["id"], sample=s, system=SYS_F,
                             user=f"Provision: {p['card']}\n\nFacts available (fields of F): " +
                                  "; ".join(f"{n} = {d}" for n, d in p["fields"]) + f"\n\nPrelude:\n{interface(p)}"))
        if not a.no_extract:
            for t in p["tests"]:
                jobs.append(dict(kind="extract", prov=p["id"], case=t["case"], system=SYS_E,
                                 user=f"Provision: {p['card']}\n\nFields: " + "; ".join(f"{n} = {d}" for n, d in p["fields"]) +
                                      f"\n\nCase:\n{cases[t['case']]['question']}"))

    def run(j):
        text, usage, err = gemini.call(a.key, a.model, j["system"], j["user"])
        return dict({k: v for k, v in j.items() if k not in ("system", "user")}, text=text, usage=usage, error=err, model=a.model)

    with cf.ThreadPoolExecutor(a.conc) as ex, open(a.out, "w") as f:
        for r in ex.map(run, jobs):
            f.write(json.dumps(r) + "\n"); f.flush()
    print("done", len(jobs))


if __name__ == "__main__":
    main()
