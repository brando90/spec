namespace Leg
inductive V | elig | notElig | inconc deriving DecidableEq, Repr

structure F where
  quitNearOldEnd : Bool
  newStartSoon : Bool
  newJobLonger : Bool
  newSeparationFullAward : Bool

structure P where
  quitNearOldEnd : Option Bool
  newStartSoon : Option Bool
  newJobLonger : Option Bool
  newSeparationFullAward : Option Bool

def opts : Option Bool → List Bool
  | some b => [b]
  | none => [true, false]

def completions (p : P) : List F :=
  (opts p.quitNearOldEnd).flatMap fun quitNearOldEnd => (opts p.newStartSoon).flatMap fun newStartSoon => (opts p.newJobLonger).flatMap fun newJobLonger => (opts p.newSeparationFullAward).flatMap fun newSeparationFullAward => [⟨quitNearOldEnd, newStartSoon, newJobLonger, newSeparationFullAward⟩]

def verdict (rule : F → Bool) (p : P) : V :=
  let o := (completions p).map rule
  if o.all id then V.elig else if o.all (fun x => !x) then V.notElig else V.inconc
def rule (f : F) : Bool :=
  f.quitNearOldEnd && f.newStartSoon && f.newJobLonger && f.newSeparationFullAward

example : verdict rule ⟨some true, some true, some true, some true⟩ = V.elig := by decide  -- case 121
example : verdict rule ⟨none, none, none, some false⟩ = V.notElig := by decide  -- case 122
example : verdict rule ⟨some true, some true, some true, none⟩ = V.inconc := by decide  -- case 123
example : verdict rule ⟨none, none, some true, none⟩ = V.inconc := by decide  -- case 124

end Leg
