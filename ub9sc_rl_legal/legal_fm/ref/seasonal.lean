namespace Leg
inductive V | elig | notElig | inconc deriving DecidableEq, Repr

structure F where
  designatedEmployer : Bool
  workedOutsidePeriod : Bool
  regained : Bool

structure P where
  designatedEmployer : Option Bool
  workedOutsidePeriod : Option Bool
  regained : Option Bool

def opts : Option Bool → List Bool
  | some b => [b]
  | none => [true, false]

def completions (p : P) : List F :=
  (opts p.designatedEmployer).flatMap fun designatedEmployer => (opts p.workedOutsidePeriod).flatMap fun workedOutsidePeriod => (opts p.regained).flatMap fun regained => [⟨designatedEmployer, workedOutsidePeriod, regained⟩]

def verdict (rule : F → Bool) (p : P) : V :=
  let o := (completions p).map rule
  if o.all id then V.elig else if o.all (fun x => !x) then V.notElig else V.inconc
def rule (f : F) : Bool :=
  f.designatedEmployer && (!f.workedOutsidePeriod || f.regained)

example : verdict rule ⟨some true, some false, none⟩ = V.elig := by decide  -- case 98
example : verdict rule ⟨some true, some true, some false⟩ = V.notElig := by decide  -- case 99
example : verdict rule ⟨some true, some true, some true⟩ = V.elig := by decide  -- case 100
example : verdict rule ⟨some true, some false, none⟩ = V.elig := by decide  -- case 101
example : verdict rule ⟨none, none, none⟩ = V.inconc := by decide  -- case 102
example : verdict rule ⟨some true, none, none⟩ = V.inconc := by decide  -- case 103

end Leg
