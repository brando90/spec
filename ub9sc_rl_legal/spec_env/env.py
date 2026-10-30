"""Idea 1: Gym-style RL environment over the 250 reglab/spec cases (natural language, no retrieval by default).

reset(i) -> observation (prompt); step(action_text) -> (reward, info). One-step episodes.
Reward: 1 if the parsed label equals the gold label, else 0. info['presumptuous'] flags a decisive answer on a case
whose gold is Inconclusive. Report complete-case and inconclusive-case accuracy separately, never one alone.
"""
import json, pathlib
from .scorer import score

HERE = pathlib.Path(__file__).parent
SYSTEM = (
    "You are a Colorado unemployment-insurance adjudicator. Decide from the case facts and Colorado UI law. "
    "If a fact you need to decide is missing from the case, do not assume it: the answer is INCONCLUSIVE and you "
    "list the missing facts. Reply in this format: first line 'DETERMINATION: <ELIGIBLE | NOT ELIGIBLE | INCONCLUSIVE>' "
    "(use YES or NO instead of ELIGIBLE / NOT ELIGIBLE when the question is a yes/no question rather than about "
    "eligibility), then 'REASON:' in at most three sentences, then for INCONCLUSIVE 'MISSING:' with the missing facts."
)


class LegalEnv:
    def __init__(self, cases_path=HERE / "cases.json", indices=None):
        self.cases = json.load(open(cases_path))
        self.indices = indices if indices is not None else list(range(len(self.cases)))
        self.cur = None

    def __len__(self):
        return len(self.indices)

    def reset(self, k):
        self.cur = self.cases[self.indices[k]]
        return dict(system=SYSTEM, user=self.cur["question"])

    def step(self, action_text):
        info = score(action_text, self.cur["answer"], self.cur["question"])
        info["no"] = self.cur["no"]
        return float(info["correct"]), info
