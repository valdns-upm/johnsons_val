"""L-curve: data misfit (J0) vs regularization term (Jreg) across Lambda values.

Usage:
    python3 plot_lcurve.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ITER = 45  # all runs read at this iteration - past the ~31 convergence plateau

# label -> (Lambda, dir holding Cost_steady.dat/CostReg_steady.dat)
# 1e4 is excluded from the plot: it diverges (J0 ~1e58, unstable optimizer
# run, not a converged point) - see docs/lambda/line_search_diagnosis.md. Still
# printed below for the record.
EXCLUDED = {
    "1e4":  (1.0e4,  "lcurve/1e4"),
}
RUNS = {
    "3e4":  (3.16e4, "lcurve/3e4"),
    "1e5":  (1.0e5,  "."),            # chosen value, from the main confirmation run
    "3e5":  (3.16e5, "lcurve/3e5"),
    "1e6":  (1.0e6,  "lcurve/1e6"),
    "3e6":  (3.16e6, "lcurve/3e6"),
    "1e7":  (1.0e7,  "lcurve/1e7"),
    "3e7":  (3.16e7, "lcurve/3e7"),
    "1e8":  (1.0e8,  "lcurve/1e8"),
}

CHOSEN = "1e5"
OUTPUT_FILE = "docs/lambda/lcurve.png"


def read_at_iter(path, iter_):
    data = np.loadtxt(path)
    row = data[data[:, 0] == iter_]
    if len(row) == 0:
        raise ValueError(f"iteration {iter_} not found in {path}")
    return row[0, 1]


def main():
    for label, (lam, d) in EXCLUDED.items():
        j0 = read_at_iter(f"{d}/Cost_steady.dat", ITER)
        jreg = read_at_iter(f"{d}/CostReg_steady.dat", ITER)
        print(f"Lambda={lam:.3g}  J0={j0:.4e}  Jreg={jreg:.4e}  (excluded: diverged)")

    lambdas, j0s, jregs, labels = [], [], [], []
    for label, (lam, d) in RUNS.items():
        j0 = read_at_iter(f"{d}/Cost_steady.dat", ITER)
        jreg = read_at_iter(f"{d}/CostReg_steady.dat", ITER)
        lambdas.append(lam)
        j0s.append(j0)
        jregs.append(jreg)
        labels.append(label)
        print(f"Lambda={lam:.3g}  J0={j0:.4e}  Jreg={jreg:.4e}")

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(jregs, j0s, "o-", color="C0")
    for lam_label, x, y in zip(labels, jregs, j0s):
        marker_color = "C3" if lam_label == CHOSEN else "C0"
        ax.plot(x, y, "o", color=marker_color)
        ax.annotate(lam_label, (x, y), textcoords="offset points", xytext=(6, 4))

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Jreg (regularization term)")
    ax.set_ylabel("J0 (data misfit)")
    ax.set_title(f"L-curve at iteration {ITER}")
    fig.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=120)
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
