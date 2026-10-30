"""Fixed scorer for the reglab/spec benchmark.

The repo's run_benchmark.py scores by substring ("eligible" in "not eligible" is a hit). This one parses one label
and compares it exactly.
"""
import re

LABELS = ["NOT ELIGIBLE", "ELIGIBLE", "INCONCLUSIVE", "YES", "NO"]


def norm_gold(answer: str) -> str:
    a = answer.strip().upper()
    return {"INELIGIBLE": "NOT ELIGIBLE"}.get(a, a)


def parse_label(text: str) -> str:
    """Label after 'DETERMINATION:' if present, else the first label word in the text; '' if none."""
    t = text.upper()
    m = re.search(r"DETERMINATION\s*[:\-]\s*\**\s*(NOT ELIGIBLE|INELIGIBLE|ELIGIBLE|INCONCLUSIVE|YES|NO)\b", t)
    if m:
        return norm_gold(m.group(1))
    m = re.search(r"\b(NOT ELIGIBLE|INELIGIBLE|ELIGIBLE|INCONCLUSIVE|YES|NO)\b", t)
    return norm_gold(m.group(1)) if m else ""


def score(text: str, gold: str, question: str = "") -> dict:
    pred, g = parse_label(text), norm_gold(gold)
    if "eligible" in question.lower():  # eligibility question: a bare YES/NO means ELIGIBLE / NOT ELIGIBLE
        pred = {"YES": "ELIGIBLE", "NO": "NOT ELIGIBLE"}.get(pred, pred)
    return dict(pred=pred, gold=g, correct=pred == g,
                presumptuous=(g == "INCONCLUSIVE" and pred not in ("INCONCLUSIVE", "")),
                substring_correct=g.lower() in text.lower())  # the repo's original rule, for comparison
