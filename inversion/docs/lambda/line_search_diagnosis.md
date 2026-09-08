# Line search stall - cause and fix

Symptom: 
"ALL DONE" but freeze after a few iterations - m1qn3 line search burns nsim
budget on step attempts (50-70 backtracks), none accepted. Cost/alpha frozen.

Cause: 
1-2 mesh nodes push alpha to extreme values (log10(C) ~ beyond +/-5): either extreme friction or almost none =>
Stokes solver locally numerically unstable => 
Cost not the same twice between backtracks =>
No accepted step: no step satisfying M1QN3 cost reduction criteria: ++ backtracks unsuccesfuls

Verification:
Checked w/ inspect_vtu_field.py on alpha across
snapshots: same node(s) every time.

Root cause: 
Lambda (Adjoint_CostRegSolver) too weak for data density (14-18
GPS pts) => nothing smooths alpha at poorly-constrained nodes. 

Fix: 
Increase Lambda => narrowed the interval (bisection): 1e4 diverges, 1e6 clean => Lambda=1e5.
Independent of GPS campaign (same data density/mesh) => no re-bisect needed,
just recheck if mesh or solver tolerances change.

Quantitative justification of 1e5: see ../lambda/lcurve.md.
