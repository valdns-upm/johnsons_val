# Choice of the regularization weight (Lambda)

The inversion recovers basal friction (`alpha = log10(C)` in the Weertman
law) by minimizing a cost function with two terms: the misfit between
modeled and observed surface velocities (`J0`), and a Tikhonov-style
smoothness penalty on `alpha` (`Jreg`, the squared norm of its gradient).
The two are combined as `J = J0 + Lambda * Jreg`. `Lambda` controls the
trade-off: too small, and the inversion overfits sparse GPS data,
pushing `alpha` to extreme, physically meaningless values at
poorly-constrained nodes; too large, and the friction field is
oversmoothed, degrading the fit to real velocity variations.

`Lambda` was chosen using the L-curve method (Hansen, 1998), the
standard approach for this trade-off: run the inversion at a range of
`Lambda` values and plot `J0` against `Jreg` on a log-log scale. The
plot typically traces an L shape - a flat region where reducing `Lambda`
barely improves the fit (regularization-dominated), and a rising branch
where reducing `Lambda` further only overfits (data-dominated). The
corner between the two marks the best trade-off.

We swept `Lambda` from 3.16e4 to 1e8 (all other settings - mesh,
solver tolerances - fixed to the production configuration), each run
carried to iteration 45, past the point where the cost stops improving.
The resulting curve (`lcurve.png`) has a clear corner at `Lambda = 1e5`:
below it, `Jreg` falls sharply for almost no change in `J0`; above it,
`J0` rises steadily as the fit degrades.

This agrees with an independent, purely numerical criterion: `Lambda`
values below roughly 3e4 make the underlying Stokes problem
numerically unstable at nodes with little GPS coverage, and the optimizer's
line search fails to converge (see `line_search_diagnosis.md`). The
L-curve corner and the stability threshold land at essentially the same
value, which is why `Lambda = 1e5` was adopted for all inversions in
this study - including across different GPS campaign years, since the
data density and mesh that drive this trade-off do not change between
campaigns.

## Reference

Hansen, P. C. (1998). *Rank-Deficient and Discrete Ill-Posed Problems:
Numerical Aspects of Linear Inversion*. SIAM Monographs on Mathematical
Modeling and Computation. Philadelphia: SIAM.
