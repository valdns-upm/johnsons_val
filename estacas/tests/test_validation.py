import pandas as pd
import pytest

from src.validation import evaluate_prediction_with_validation


def test_evaluate_prediction_with_validation_rmse_zero_for_constant_velocity():
    train_df = pd.DataFrame([
        {"stake_id": "EJ1", "date": pd.Timestamp("2020-01-01"), "x": 0, "y": 0, "glacier": "johnson"},
    ])
    displacements = pd.DataFrame([
        {"stake_id": "EJ1", "date_end": pd.Timestamp("2019-01-01"), "dt_days": 365, "dx": 365, "dy": 0},
    ])
    # Observed position exactly matches vx=1 m/day, vy=0 carried forward -> zero prediction error.
    validation_df = pd.DataFrame([
        {"stake_id": "EJ1", "date": pd.Timestamp("2021-01-01"), "x": 366, "y": 0},
    ])

    summary, details = evaluate_prediction_with_validation(train_df, validation_df, displacements)

    assert summary.iloc[0]["n_stakes"] == 1
    assert summary.iloc[0]["rmse_dist_m"] == pytest.approx(0.0)
