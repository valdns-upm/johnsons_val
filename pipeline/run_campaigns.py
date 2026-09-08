"""Run estacas -> kriging -> inversion for a list of campaign tags.

Usage (from repo root):
    python pipeline/run_campaigns.py 1517 2224

estacas and kriging run in sequence for each tag (seconds). Each
inversion is launched in its own tmux session and NOT waited on - use
inversion/scripts/check_run.sh or `tmux ls` to follow it afterwards.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "estacas"))

from campaigns import CAMPAIGNS, source_dirs  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402

KRIGING_DIR = ROOT / "kriging"
KRIGING_GRID = KRIGING_DIR / "input" / "johnsons_mesh_grid.dat"
INVERSION_DIR = ROOT / "inversion"
SIF_TEMPLATE = INVERSION_DIR / "johnsons_inversion.template.sif"
MESH_CHECKPOINT_DIR = "mesh_Johnson_gmsh_2D_100_front_refined"


def run_estacas_stage(tag):
    output_dir = ROOT / "estacas" / "output" / tag
    run_pipeline(
        data_paths=source_dirs(tag),
        output_dir=output_dir,
        campaign_tag=tag,
    )
    return output_dir


def run_kriging_stage(tag, estacas_output_dir):
    kriged_paths = {}
    for component in ("vx", "vy"):
        data_file = estacas_output_dir / f"johnsons_{component}_{tag}_smooth.dat"
        output_file = KRIGING_DIR / "output" / f"johnsons_{component}_kriged_{tag}_smooth.dat"
        subprocess.run(
            [
                sys.executable, "ClsMain.py", "--headless",
                "--semi", str(data_file),
                "--krige", str(data_file),
                "--grid", str(KRIGING_GRID),
                "--output", str(output_file),
            ],
            cwd=KRIGING_DIR,
            check=True,
        )
        kriged_paths[component] = output_file
    return kriged_paths


def tmux_session_active(session_name):
    result = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    return result.returncode == 0


def run_inversion_stage(tag):
    session_name = f"camp_{tag}"
    run_dir = INVERSION_DIR / session_name

    if tmux_session_active(session_name):
        print(f"[{tag}] tmux session '{session_name}' already running - skipping inversion.")
        return None

    if run_dir.exists():
        print(f"[{tag}] {run_dir} already exists - not overwriting. Remove it manually to rerun.")
        return None

    run_dir.mkdir(parents=True)
    (run_dir / "results").mkdir()
    (run_dir / MESH_CHECKPOINT_DIR).mkdir()

    sif_text = SIF_TEMPLATE.read_text().replace("{{TAG}}", tag)
    (run_dir / "johnsons_inversion.sif").write_text(sif_text)

    subprocess.run(
        [
            "tmux", "new-session", "-d", "-s", session_name, "-c", str(run_dir),
            "ElmerSolver johnsons_inversion.sif > run_full.log 2>&1",
        ],
        check=True,
    )
    print(f"[{tag}] inversion launched in tmux session '{session_name}' ({run_dir})")
    return session_name


def main(tags):
    launched = []
    for tag in tags:
        if tag not in CAMPAIGNS:
            print(f"[{tag}] unknown tag, not in pipeline/campaigns.py - skipping.")
            continue

        print(f"[{tag}] estacas...")
        estacas_output_dir = run_estacas_stage(tag)

        print(f"[{tag}] kriging...")
        run_kriging_stage(tag, estacas_output_dir)

        print(f"[{tag}] inversion...")
        session_name = run_inversion_stage(tag)
        if session_name:
            launched.append(session_name)

    if launched:
        print("\nInversions running:", ", ".join(launched))
        print("Follow with: tmux ls / tmux attach -t <session> / bash inversion/scripts/check_run.sh (from the run dir)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline/run_campaigns.py <tag> [<tag> ...]")
        sys.exit(1)
    main(sys.argv[1:])
