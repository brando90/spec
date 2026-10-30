"""Idea 2, phase 2 (local, Lean only): kernel-check generated rules and score extractions.
Usage: python3 -m legal_fm.check_formal gens.jsonl [--lean lean]
formalize: build the Lean file (prelude + model rule + hidden dataset-grounded tests), run lean, count tests whose line has no error.
extract: compare facts to gold; verdict from the reference rule (mirrors the Lean-checked reference).
"""
import argparse, json, pathlib, re, subprocess, tempfile, collections, os
from .gen_lean import build

HERE = pathlib.Path(__file__).parent


def strip_fences(t):
    t = re.sub(r"^```[a-z]*\n|```\s*$", "", t.strip(), flags=re.M).strip()
    return t


def lean_check(p, rule_text, lean):
    rt = strip_fences(rule_text)
    m = re.search(r"def\s+rule\s*\(f\s*:\s*F\)\s*:\s*Bool\s*:=\s*(.*)", rt, re.S)
    if not m:
        return dict(compiled=False, passed=0, total=len(p["tests"]), err="no rule def")
    src = build(p, m.group(1).strip().replace("\n", "\n  "))
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "t.lean"; f.write_text(src)
        r = subprocess.run([lean, str(f)], capture_output=True, text=True, timeout=180)
    lines = src.split("\n"); first_test = next(i for i, l in enumerate(lines) if l.startswith("example")) + 1
    errs = {int(x) for x in re.findall(r"t\.lean:(\d+):\d+: error", r.stdout + r.stderr)}
    test_lines = range(first_test, first_test + len(p["tests"]))
    rule_err = [e for e in errs if e < first_test]
    if rule_err:
        return dict(compiled=False, passed=0, total=len(p["tests"]), err=(r.stdout + r.stderr)[:300])
    failed = sum(1 for e in test_lines if e in errs)
    return dict(compiled=True, passed=len(p["tests"]) - failed, total=len(p["tests"]), err="")


def ref_verdict(p, facts):
    import itertools
    names = [x[0] for x in p["fields"]]
    expr = p["ref"].replace("&&", " and ").replace("||", " or ").replace("!", " not ")
    opts = [[v] if v is not None else [True, False] for v in facts]
    outs = [eval(expr, {}, {"f": type("F", (), dict(zip(names, c)))()}) for c in itertools.product(*opts)]
    return "elig" if all(outs) else "notElig" if not any(outs) else "inconc"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("gens"); ap.add_argument("--lean", default="lean")
    a = ap.parse_args()
    env = dict(os.environ); env["PATH"] = os.path.expanduser("~/.elan/bin") + ":" + env["PATH"]; os.environ.update(env)
    spec = {p["id"]: p for p in json.load(open(HERE / "provisions.json"))["provisions"]}
    rows = [json.loads(l) for l in open(a.gens)]
    fm = collections.defaultdict(list); ex = collections.defaultdict(list)
    for r in rows:
        if r["error"]:
            print("error", r["kind"], r["prov"], r["error"][:100]); continue
        p = spec[r["prov"]]
        if r["kind"] == "formalize":
            res = lean_check(p, r["text"], a.lean); res["sample"] = r["sample"]; fm[r["prov"]].append(res)
        else:
            t = next(t for t in p["tests"] if t["case"] == r["case"])
            m = re.search(r"\{.*\}", r["text"], re.S)
            try:
                d = json.loads(m.group(0)); facts = [d.get(n) for n, _ in p["fields"]]
            except Exception:
                facts = None
            ok_facts = facts == t["facts"]
            ok_verdict = facts is not None and ref_verdict(p, facts) == t["gold"]
            ex[r["prov"]].append(dict(case=r["case"], facts_exact=ok_facts, verdict=ok_verdict))
    print("FORMALIZE (Lean kernel; tests hidden from the model)")
    tot = allp = n = 0
    for k, v in fm.items():
        print(f"  {k}: compiled {sum(x['compiled'] for x in v)}/{len(v)}; all tests pass {sum(x['compiled'] and x['passed']==x['total'] for x in v)}/{len(v)}; tests passed {sum(x['passed'] for x in v)}/{sum(x['total'] for x in v)}")
        tot += sum(x["compiled"] for x in v); allp += sum(x["compiled"] and x["passed"] == x["total"] for x in v); n += len(v)
    print(f"  total: compiled {tot}/{n}; all tests pass {allp}/{n}")
    print("EXTRACT (case text -> facts -> verdict)")
    ne = nf = nv = 0
    for k, v in ex.items():
        print(f"  {k}: facts exact {sum(x['facts_exact'] for x in v)}/{len(v)}; verdict correct {sum(x['verdict'] for x in v)}/{len(v)}; wrong: {[x['case'] for x in v if not x['verdict']]}")
        ne += len(v); nf += sum(x["facts_exact"] for x in v); nv += sum(x["verdict"] for x in v)
    print(f"  total: facts exact {nf}/{ne}; verdict correct {nv}/{ne}")
    json.dump(dict(formalize=fm, extract=ex), open(a.gens + ".scored.json", "w"), indent=1)


if __name__ == "__main__":
    main()
