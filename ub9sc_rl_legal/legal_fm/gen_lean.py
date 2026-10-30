"""Generate Lean 4 checker files from provisions.json (no Mathlib needed).

Per provision: Facts structure (Bool fields), partial-facts structure (Option Bool), completions, the three-valued
verdict (Eligible if every completion satisfies the rule, Not Eligible if none does, else Inconclusive), a `rule`
(the reference one or a model's), and one `example ... := by decide` per dataset-grounded test, one per line so
failures can be counted by line number.
"""
import json, pathlib, itertools

HERE = pathlib.Path(__file__).parent
VN = {"elig": "V.elig", "notElig": "V.notElig", "inconc": "V.inconc"}


def prelude(p):
    fs = [f[0] for f in p["fields"]]
    L = ["namespace Leg", "inductive V | elig | notElig | inconc deriving DecidableEq, Repr", ""]
    L += ["structure F where"] + [f"  {n} : Bool" for n in fs] + ["", "structure P where"] + [f"  {n} : Option Bool" for n in fs] + [""]
    L += ["def opts : Option Bool → List Bool", "  | some b => [b]", "  | none => [true, false]", ""]
    body = "[⟨" + ", ".join(fs) + "⟩]"
    for n in reversed(fs):
        body = f"(opts p.{n}).flatMap fun {n} => {body}"
    L += ["def completions (p : P) : List F :=", f"  {body}", ""]
    L += ["def verdict (rule : F → Bool) (p : P) : V :=", "  let o := (completions p).map rule",
          "  if o.all id then V.elig else if o.all (fun x => !x) then V.notElig else V.inconc", ""]
    return "\n".join(L)


def tests(p):
    out = []
    for t in p["tests"]:
        args = ", ".join("none" if v is None else f"some {str(v).lower()}" for v in t["facts"])
        out.append(f"example : verdict rule ⟨{args}⟩ = {VN[t['gold']]} := by decide  -- case {t['case']}")
    return "\n".join(out)


def build(p, rule_body):
    return prelude(p) + f"def rule (f : F) : Bool :=\n  {rule_body}\n\n" + tests(p) + "\n\nend Leg\n"


def interface(p):
    """What the model sees: prelude without tests, and the rule's signature."""
    return prelude(p) + "-- write: def rule (f : F) : Bool := ...\n"


if __name__ == "__main__":
    spec = json.load(open(HERE / "provisions.json"))
    (HERE / "ref").mkdir(exist_ok=True)
    for p in spec["provisions"]:
        (HERE / "ref" / f"{p['id']}.lean").write_text(build(p, p["ref"]))
