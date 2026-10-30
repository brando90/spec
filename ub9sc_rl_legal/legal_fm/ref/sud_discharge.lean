namespace Leg
inductive V | elig | notElig | inconc deriving DecidableEq, Repr

structure F where
  nonVolitional : Bool
  directlyDue : Bool
  declared : Bool
  documentation : Bool
  treatmentWithin4Weeks : Bool

structure P where
  nonVolitional : Option Bool
  directlyDue : Option Bool
  declared : Option Bool
  documentation : Option Bool
  treatmentWithin4Weeks : Option Bool

def opts : Option Bool → List Bool
  | some b => [b]
  | none => [true, false]

def completions (p : P) : List F :=
  (opts p.nonVolitional).flatMap fun nonVolitional => (opts p.directlyDue).flatMap fun directlyDue => (opts p.declared).flatMap fun declared => (opts p.documentation).flatMap fun documentation => (opts p.treatmentWithin4Weeks).flatMap fun treatmentWithin4Weeks => [⟨nonVolitional, directlyDue, declared, documentation, treatmentWithin4Weeks⟩]

def verdict (rule : F → Bool) (p : P) : V :=
  let o := (completions p).map rule
  if o.all id then V.elig else if o.all (fun x => !x) then V.notElig else V.inconc
def rule (f : F) : Bool :=
  f.nonVolitional && f.directlyDue && f.declared && f.documentation && f.treatmentWithin4Weeks

example : verdict rule ⟨some true, some true, some true, some true, some true⟩ = V.elig := by decide  -- case 1
example : verdict rule ⟨some true, some true, some true, some true, some false⟩ = V.notElig := by decide  -- case 2
example : verdict rule ⟨some true, none, some true, some true, some true⟩ = V.inconc := by decide  -- case 3
example : verdict rule ⟨some true, some true, some true, some true, some true⟩ = V.elig := by decide  -- case 4
example : verdict rule ⟨none, none, some true, some true, some true⟩ = V.inconc := by decide  -- case 5
example : verdict rule ⟨none, none, some true, some true, none⟩ = V.inconc := by decide  -- case 6

end Leg
