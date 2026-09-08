import pandas as pd

from src.trajectory import build_trajectories, compute_displacements


def test_compute_displacements_drops_outlier_and_bridges_segment():
    df = pd.DataFrame([
        {"stake_id": "EJ1", "date": pd.Timestamp("2020-01-01"), "x": 0, "y": 0, "z": 0, "glacier": "johnson"},
        {"stake_id": "EJ1", "date": pd.Timestamp("2020-01-02"), "x": 100, "y": 0, "z": 0, "glacier": "johnson"},
        {"stake_id": "EJ1", "date": pd.Timestamp("2020-01-03"), "x": 2, "y": 0, "z": 0, "glacier": "johnson"},
    ])

    trajectories = build_trajectories(df)
    cleaned, displacements, issues = compute_displacements(trajectories)

    assert len(cleaned["EJ1"]) == 2
    assert list(cleaned["EJ1"]["x"]) == [0, 2]

    outliers = issues[issues["issue_type"] == "OUTLIER"]
    assert len(outliers) == 1
    assert outliers.iloc[0]["date"] == pd.Timestamp("2020-01-02")

    assert len(displacements) == 1
    row = displacements.iloc[0]
    assert row["dt_days"] == 2
    assert row["dx"] == 2
    assert row["daily_segment_speed"] == 1.0
