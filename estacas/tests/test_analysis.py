import pandas as pd

from src.analysis import aggregate_window_velocity, build_prediction_status


def test_aggregate_window_velocity_excludes_too_few_segments():
    # window_years=3 -> min_segments=2. EJ1 has 2 segments, EJ2 has 1.
    displacements = pd.DataFrame([
        {"stake_id": "EJ1", "glacier": "johnson", "date_start": pd.Timestamp("2016-06-01"),
         "date_end": pd.Timestamp("2017-06-01"), "x": 0, "y": 0, "dt_days": 365, "dx": 0, "dy": 0},
        {"stake_id": "EJ1", "glacier": "johnson", "date_start": pd.Timestamp("2017-06-01"),
         "date_end": pd.Timestamp("2019-06-01"), "x": 0, "y": 0, "dt_days": 730, "dx": 730, "dy": 0},
        {"stake_id": "EJ2", "glacier": "johnson", "date_start": pd.Timestamp("2017-06-01"),
         "date_end": pd.Timestamp("2019-06-01"), "x": 0, "y": 0, "dt_days": 730, "dx": 730, "dy": 0},
    ])

    aggregated, n_candidates, n_included = aggregate_window_velocity(
        displacements, target_date="2020-01-01", window_years=3
    )

    assert n_candidates == 2
    assert n_included == 1
    assert list(aggregated["stake_id"]) == ["EJ1"]

    ej1 = aggregated.iloc[0]
    assert ej1["n_segments"] == 2
    assert ej1["window_start"] == pd.Timestamp("2016-06-01")


def test_aggregate_window_velocity_includes_stake_missing_one_year():
    # EJ3 has no segment reaching back to the window's start (it's missing
    # from the earliest file) but still has 2 consecutive segments - enough
    # to be included, not excluded for lacking the full window.
    displacements = pd.DataFrame([
        {"stake_id": "EJ3", "glacier": "johnson", "date_start": pd.Timestamp("2018-01-01"),
         "date_end": pd.Timestamp("2019-01-01"), "x": 0, "y": 0, "dt_days": 365, "dx": 0, "dy": 0},
        {"stake_id": "EJ3", "glacier": "johnson", "date_start": pd.Timestamp("2019-01-01"),
         "date_end": pd.Timestamp("2020-01-01"), "x": 0, "y": 0, "dt_days": 365, "dx": 0, "dy": 0},
    ])

    aggregated, _, n_included = aggregate_window_velocity(
        displacements, target_date="2020-01-01", window_years=3
    )

    assert n_included == 1
    assert aggregated.iloc[0]["n_segments"] == 2


def test_aggregate_window_velocity_uses_all_loaded_segments_once_eligible():
    # EJ1 has more history than window_years - nothing should clip it.
    displacements = pd.DataFrame([
        {"stake_id": "EJ1", "glacier": "johnson", "date_start": pd.Timestamp("2015-12-01"),
         "date_end": pd.Timestamp("2016-12-01"), "x": 0, "y": 0, "dt_days": 366, "dx": 0, "dy": 0},
        {"stake_id": "EJ1", "glacier": "johnson", "date_start": pd.Timestamp("2016-12-01"),
         "date_end": pd.Timestamp("2017-12-01"), "x": 0, "y": 0, "dt_days": 365, "dx": 0, "dy": 0},
        {"stake_id": "EJ1", "glacier": "johnson", "date_start": pd.Timestamp("2017-12-01"),
         "date_end": pd.Timestamp("2018-12-01"), "x": 0, "y": 0, "dt_days": 365, "dx": 0, "dy": 0},
        {"stake_id": "EJ1", "glacier": "johnson", "date_start": pd.Timestamp("2018-12-01"),
         "date_end": pd.Timestamp("2019-12-01"), "x": 0, "y": 0, "dt_days": 365, "dx": 0, "dy": 0},
    ])

    aggregated, _, _ = aggregate_window_velocity(
        displacements, target_date="2020-01-01", window_years=3
    )

    ej1 = aggregated.iloc[0]
    assert ej1["n_segments"] == 4
    assert ej1["window_start"] == pd.Timestamp("2015-12-01")


def test_build_prediction_status_lost_and_single_measurement():
    df = pd.DataFrame([
        {"stake_id": "EJ1", "date": pd.Timestamp("2019-01-01"), "source_order": 1},
        {"stake_id": "EJ1", "date": pd.Timestamp("2020-01-01"), "source_order": 2},
        {"stake_id": "EJ2", "date": pd.Timestamp("2020-01-01"), "source_order": 2},
    ])
    monitoring_df = pd.DataFrame([
        {"stake_id": "EJ1", "is_lost": True, "source_order": 2,
         "date": pd.Timestamp("2020-01-01"), "gps_comment": "ESTACA PERDIDA", "source_file": "f2.xlsx"},
    ])

    status = build_prediction_status(df, monitoring_df, displacements=pd.DataFrame()).set_index("stake_id")

    assert status.loc["EJ1", "prediction_status"] == "unpredicted"
    assert status.loc["EJ1", "prediction_status_detail"] == "lost"
    assert status.loc["EJ2", "prediction_status"] == "unpredicted"
    assert status.loc["EJ2", "prediction_status_detail"] == "single measurement"
