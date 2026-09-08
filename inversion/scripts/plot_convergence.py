"""Plot cost and gradient-norm history from an Elmer inversion run.

Usage:
    python3 plot_convergence.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

COST_FILE = "Cost_steady.dat"
GRADNORM_FILE = "GradientNormAdjoint_steady.dat"
OUTPUT_FILE = "convergence.png"  # Change to save under a different name


def main():
    cost = np.loadtxt(COST_FILE)
    gradnorm = np.loadtxt(GRADNORM_FILE)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.plot(cost[:, 0], cost[:, 1])
    ax1.set_xlabel("evaluation")
    ax1.set_ylabel("cost J0")
    ax1.set_title("Cost")

    ax2.plot(gradnorm[:, 0], gradnorm[:, 1])
    ax2.set_xlabel("evaluation")
    ax2.set_ylabel("gradient norm")
    ax2.set_yscale("log")
    ax2.set_title("Gradient norm")

    fig.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=120)
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
