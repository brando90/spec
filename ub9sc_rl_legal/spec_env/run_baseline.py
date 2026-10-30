"""Test 0: zero-shot Gemini baseline on the reglab/spec cases with the fixed scorer, no retrieval.

Usage: python3 -m spec_env.run_baseline --model gemini-3-flash-preview --key /path/key.txt --out out.jsonl [--n 250] [--conc 4]
"""
import argparse, json, concurrent.futures as cf, collections
from .env import LegalEnv
from . import gemini


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--key", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=250); ap.add_argument("--conc", type=int, default=4)
    ap.add_argument("--stride", type=int, default=1, help="take every stride-th case (stratified subsample)")
    a = ap.parse_args()
    idx = list(range(0, 250, a.stride))[: a.n]
    done = {}
    try:
        for l in open(a.out):
            r = json.loads(l)
            if not r.get("error"): done[r["no"]] = r
    except FileNotFoundError:
        pass
    env = LegalEnv(indices=idx)

    def one(k):
        e = LegalEnv(indices=idx); obs = e.reset(k)
        if e.cur["no"] in done: return done[e.cur["no"]]
        text, usage, err = gemini.call(a.key, a.model, obs["system"], obs["user"])
        reward, info = e.step(text)
        return dict(info, reward=reward, text=text, usage=usage, error=err, model=a.model)

    rows = []
    with cf.ThreadPoolExecutor(a.conc) as ex, open(a.out, "a") as f:  # append + as completed: a hung call blocks nothing, a rerun resumes
        futs = [ex.submit(one, k) for k in range(len(env))]
        for fu in cf.as_completed(futs):
            r = fu.result()
            if r["no"] not in done: f.write(json.dumps(r) + "\n"); f.flush()
            rows.append(r)
    ok = [r for r in rows if not r["error"]]
    comp = [r for r in ok if r["gold"] != "INCONCLUSIVE"]; inc = [r for r in ok if r["gold"] == "INCONCLUSIVE"]
    acc = lambda rs, k="correct": f"{sum(r[k] for r in rs)}/{len(rs)}" + (f" ({sum(r[k] for r in rs)/len(rs):.3f})" if rs else "")
    print(f"model {a.model}  scored {len(ok)}/{len(rows)} (errors {len(rows)-len(ok)})")
    print("overall      ", acc(ok)); print("complete     ", acc(comp)); print("inconclusive ", acc(inc))
    print("presumptuous (decisive on inconclusive)", acc(inc, "presumptuous"))
    print("substring-scorer overall (repo's rule)", acc(ok, "substring_correct"))
    print("tokens in/out", sum(r["usage"].get("promptTokenCount", 0) for r in ok), sum(r["usage"].get("candidatesTokenCount", 0) + r["usage"].get("thoughtsTokenCount", 0) for r in ok))
    print("confusion", dict(collections.Counter((r["gold"], r["pred"]) for r in ok)))


if __name__ == "__main__":
    main()
