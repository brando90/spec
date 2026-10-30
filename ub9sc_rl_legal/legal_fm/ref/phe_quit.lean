namespace Leg
inductive V | elig | notElig | inconc deriving DecidableEq, Repr

structure F where
  emergencyDeclared : Bool
  immunocompromised : Bool
  providerEvidence : Bool

structure P where
  emergencyDeclared : Option Bool
  immunocompromised : Option Bool
  providerEvidence : Option Bool

def opts : Option Bool → List Bool
  | some b => [b]
  | none => [true, false]

def completions (p : P) : List F :=
  (opts p.emergencyDeclared).flatMap fun emergencyDeclared => (opts p.immunocompromised).flatMap fun immunocompromised => (opts p.providerEvidence).flatMap fun providerEvidence => [⟨emergencyDeclared, immunocompromised, providerEvidence⟩]

def verdict (rule : F → Bool) (p : P) : V :=
  let o := (completions p).map rule
  if o.all id then V.elig else if o.all (fun x => !x) then V.notElig else V.inconc
def rule (f : F) : Bool :=
  f.emergencyDeclared && f.immunocompromised && f.providerEvidence

example : verdict rule ⟨some true, some true, some true⟩ = V.elig := by decide  -- case 104
example : verdict rule ⟨some true, some false, some false⟩ = V.notElig := by decide  -- case 105
example : verdict rule ⟨some true, some true, none⟩ = V.inconc := by decide  -- case 106
example : verdict rule ⟨some true, none, none⟩ = V.inconc := by decide  -- case 107

end Leg
