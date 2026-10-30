"""Summarize a run_baseline jsonl: python3 -m spec_env.summarize out.jsonl"""
import json, sys, collections
rs = [json.loads(l) for l in open(sys.argv[1])]
ok = [r for r in rs if not r["error"]]
comp = [r for r in ok if r["gold"] != "INCONCLUSIVE"]; inc = [r for r in ok if r["gold"] == "INCONCLUSIVE"]
acc = lambda x, k="correct": f"{sum(r[k] for r in x)}/{len(x)} ({sum(r[k] for r in x)/max(1,len(x)):.3f})"
print(f"scored {len(ok)} of {len(rs)} rows; missing case numbers: {sorted(set(range(1,251)) - {r['no'] for r in ok})}")
print("overall      ", acc(ok)); print("complete     ", acc(comp)); print("inconclusive ", acc(inc))
print("presumptuous (decisive answer on inconclusive)", acc(inc, "presumptuous"))
print("substring rule (repo) overall", acc(ok, "substring_correct"), "; inconclusive only", acc(inc, "substring_correct"), "; complete only", acc(comp, "substring_correct"))
print("tokens in/out", sum(r["usage"].get("promptTokenCount", 0) for r in ok), sum(r["usage"].get("candidatesTokenCount", 0) + r["usage"].get("thoughtsTokenCount", 0) for r in ok))
print("no label parsed:", sum(r["pred"] == "" for r in ok))
cm = collections.Counter((r["gold"], r["pred"]) for r in ok)
for k, v in sorted(cm.items()): print("  gold", k[0], "pred", k[1] or "-", v)
