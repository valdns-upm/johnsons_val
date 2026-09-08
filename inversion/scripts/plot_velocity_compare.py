"""Plot observed vs modeled surface velocity from compare_velocity.py's output.

Usage (from the campaign folder, e.g. camp_0609/):
    python3 ../scripts/plot_velocity_compare.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

INPUT_FILE = "../docs/results/0609/velocity_comparison.dat"  # edit per campaign
OUTPUT_FILE = "../docs/results/0609/velocity_comparison.png"  # edit per campaign


def main():
    d = np.loadtxt(INPUT_FILE, skiprows=1)
    x, y, vsx, vsy, v1, v2 = d.T

    speed_obs = np.hypot(vsx, vsy)
    speed_mod = np.hypot(v1, v2)
    resid = np.hypot(v1 - vsx, v2 - vsy)

    rmse = np.sqrt(np.mean(resid**2))
    bias = np.mean(speed_mod - speed_obs)
    corr = np.corrcoef(speed_obs, speed_mod)[0, 1]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    speed_vmax = max(speed_obs.max(), speed_mod.max())

    ax = axes[0]
    sc = ax.scatter(x, y, c=speed_obs, s=8, cmap="viridis", vmin=0, vmax=speed_vmax)
    ax.set_title("Observed speed (m/yr)")
    ax.set_aspect("equal")
    plt.colorbar(sc, ax=ax)

    ax = axes[1]
    sc = ax.scatter(x, y, c=speed_mod, s=8, cmap="viridis", vmin=0, vmax=speed_vmax)
    ax.set_title("Modeled speed (m/yr)")
    ax.set_aspect("equal")
    plt.colorbar(sc, ax=ax)

    ax = axes[2]
    sc = ax.scatter(x, y, c=resid, s=8, cmap="inferno")
    ax.set_title("Residual |model - obs| (m/yr)")
    ax.set_aspect("equal")
    plt.colorbar(sc, ax=ax)

    fig.suptitle(f"RMSE={rmse:.2f} m/yr, mean bias={bias:.2f} m/yr, n={len(x)} points")
    fig.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=130)
    print(f"RMSE={rmse:.3f} m/yr, bias={bias:.3f} m/yr, corr={corr:.3f}")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
