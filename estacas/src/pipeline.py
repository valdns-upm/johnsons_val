from pathlib import Path

import pandas as pd

from src.io import load_monitoring_metadata, load_multiple_files
from src.trajectory import build_trajectories, compute_displacements
from src.analysis import (
    aggregate_window_velocity,
    compute_prediction,
    compute_stake_historic,
    compute_campaign_summary,
    summarize_recent_campaigns,
)
from src.validation import evaluate_prediction_with_validation
from src.geospatial import export_geopackage


def run_pipeline(
    data_paths,
    output_dir="output",
    validation_path=None,
    run_validation=False,
    run_prediction=False,
    prediction_target_date="2026-01-10",
    smoothed_velocity_target_date=None,
    window_years=3,
    campaign_tag=None,
):
    """Run the full estacas pipeline for one set of raw campaign folders.

    data_paths: one folder or a list of folders holding the raw .xls/.xlsx
    files for this run (e.g. the red_global/campXXXXa dirs for one campaign).
    Mirrors what main.py runs interactively, parametrized so it can be
    called once per campaign by an orchestrator.
    """
    df = load_multiple_files(data_paths)
    monitoring_df = load_monitoring_metadata(data_paths)
    recent_campaigns_summary = summarize_recent_campaigns(df, n_campaigns=2)

    trajectories = build_trajectories(df)
    cleaned_trajectories, displacements, issues = compute_displacements(trajectories)

    stake_historic = compute_stake_historic(df, displacements)
    campaign_summary = compute_campaign_summary(df)

    predicted_positions = None
    if run_prediction:
        predicted_positions = compute_prediction(
            df,
            displacements,
            target_date=prediction_target_date,
            monitoring_df=monitoring_df,
        )

    validation_summary = None
    validation_details = None
    if run_validation and validation_path and any(Path(validation_path).glob("*.xlsx")):
        validation_df = load_multiple_files(validation_path)
        validation_summary, validation_details = evaluate_prediction_with_validation(
            train_df=df,
            validation_df=validation_df,
            displacements=displacements,
        )
    elif run_validation:
        print(f"Validation requested, but no .xlsx files were found in {validation_path}")

    export_results(
        cleaned_trajectories,
        displacements,
        issues,
        stake_historic,
        campaign_summary,
        predicted_positions,
        validation_summary=validation_summary,
        validation_details=validation_details,
        output_dir=output_dir,
    )

    export_kriging_inputs(
        displacements,
        output_dir=output_dir,
        start_date=None,
        end_date=None,
        velocity_unit="m_per_year",
    )

    try:
        export_smoothed_kriging_inputs(
            displacements,
            target_date=smoothed_velocity_target_date or displacements["date_end"].max(),
            window_years=window_years,
            output_dir=output_dir,
            velocity_unit="m_per_year",
            label=campaign_tag,
        )
    except ValueError as error:
        print(f"Smoothed velocity export skipped: {error}")

    print("Number of stakes monitored:", len(stake_historic))
    print(
        f"Number of stakes with data in the last two campaigns ({recent_campaigns_summary['recent_campaigns']}):",
        recent_campaigns_summary["stakes_with_recent_campaigns"],
    )
    print("Number of stakes with one measurement:", (stake_historic["n_points"] == 1).sum())
    print("Number of stakes with outliers:", issues.loc[issues["issue_type"] == "OUTLIER", "stake_id"].nunique())

    if validation_summary is not None and not validation_summary.empty:
        metrics = validation_summary.iloc[0]
        print("Validation stakes compared:", int(metrics["n_stakes"]))
        print("Validation RMSE distance:", round(float(metrics["rmse_dist_m"]), 4), "m")

    return {
        "displacements": displacements,
        "stake_historic": stake_historic,
        "campaign_summary": campaign_summary,
        "issues": issues,
        "validation_summary": validation_summary,
        "validation_details": validation_details,
    }


def export_kriging_inputs(
    displacements,
    output_dir="output",
    start_date=None,
    end_date=None,
    velocity_unit="m_per_day",
):
    """Export Johnsons stake velocities as X Y value files for kriging.

    One row is written per valid displacement segment. Coordinates are the
    midpoint of the segment, so the velocity is associated with the position
    where it is representative. The two components are exported separately.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    data = displacements.copy()
    if data.empty:
        raise ValueError("No displacement segment is available for kriging export")

    data = data[data["glacier"].astype(str).str.lower().eq("johnson")].copy()
    if start_date is not None:
        start_date = pd.Timestamp(start_date)
    if end_date is not None:
        end_date = pd.Timestamp(end_date)
    if start_date is not None:
        data = data[data["date_start"] >= start_date]
    if end_date is not None:
        data = data[data["date_end"] <= end_date]
    if data.empty:
        raise ValueError("No Johnsons displacement matches the requested period")

    # ElmerIce Johnsons uses 365.25 days per year in its time conversion.
    scale = {"m_per_day": 1.0, "m_per_year": 365.25, "m_per_second": 1.0 / 86400.0}
    if velocity_unit not in scale:
        raise ValueError(f"Unsupported velocity unit: {velocity_unit}")

    data["vx"] = data["dx"] / data["dt_days"] * scale[velocity_unit]
    data["vy"] = data["dy"] / data["dt_days"] * scale[velocity_unit]
    columns = ["x", "y"]
    data[columns + ["vx"]].to_csv(
        output_path / "johnsons_vx.dat", sep="\t", index=False, header=False,
        float_format="%.8g"
    )
    data[columns + ["vy"]].to_csv(
        output_path / "johnsons_vy.dat", sep="\t", index=False, header=False,
        float_format="%.8g"
    )

    # Keep a CSV with stake/date provenance for traceability.
    data[["stake_id", "date_start", "date_end", "x", "y", "vx", "vy"]].to_csv(
        output_path / "johnsons_velocity_metadata.csv", index=False
    )
    return data


def export_smoothed_kriging_inputs(
    displacements,
    target_date,
    window_years=3,
    output_dir="output",
    velocity_unit="m_per_year",
    label=None,
):
    """Export one multi-year-smoothed velocity point per stake.

    Unlike export_kriging_inputs (one row per raw segment), this
    aggregates all segments in the window_years preceding target_date
    into a single duration-weighted velocity per stake, reducing noise
    from any one interval. Written to separate, distinctly-named files
    so the existing per-segment kriging inputs are left untouched.

    label: file suffix identifying this export, e.g. a campaign tag
    ("1517"). Defaults to target_date's year, for manual/interactive runs
    that don't have a tag assigned.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    data, n_candidates, n_included = aggregate_window_velocity(
        displacements, target_date, window_years=window_years
    )
    if data.empty:
        raise ValueError("No stake has full window coverage for the requested period")

    scale = {"m_per_day": 1.0, "m_per_year": 365.25, "m_per_second": 1.0 / 86400.0}
    if velocity_unit not in scale:
        raise ValueError(f"Unsupported velocity unit: {velocity_unit}")

    data = data.copy()
    data["vx"] = data["vx_m_per_day"] * scale[velocity_unit]
    data["vy"] = data["vy_m_per_day"] * scale[velocity_unit]

    suffix = f"{label or pd.Timestamp(target_date).year}_smooth"
    columns = ["x", "y"]
    data[columns + ["vx"]].to_csv(
        output_path / f"johnsons_vx_{suffix}.dat", sep="\t", index=False, header=False,
        float_format="%.8g"
    )
    data[columns + ["vy"]].to_csv(
        output_path / f"johnsons_vy_{suffix}.dat", sep="\t", index=False, header=False,
        float_format="%.8g"
    )
    data[["stake_id", "x", "y", "vx", "vy", "n_segments", "window_start", "window_end"]].to_csv(
        output_path / f"johnsons_velocity_metadata_{suffix}.csv", index=False
    )

    print(
        f"Smoothed velocity ({window_years}y window ending {pd.Timestamp(target_date).date()}): "
        f"{n_included}/{n_candidates} stakes included, "
        f"{n_candidates - n_included} excluded for insufficient history."
    )
    return data


def _round_existing_columns(df, columns, decimals):
    existing_columns = [col for col in columns if col in df.columns]
    if existing_columns:
        df[existing_columns] = df[existing_columns].round(decimals)

# -------------------------------------------------------------------------
# Export all results to CSV and GeoPackage: 
# normalize and round numeric columns, handle optional validation outputs, 
# and ensure consistent formatting across all exports.
# -------------------------------------------------------------------------
def export_results(
    cleaned_trajectories,
    displacements,
    issues,
    stake_historic,
    campaign_summary,
    prediction=None,
    validation_summary=None,
    validation_details=None,
    output_dir="output",
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    stake_historic_path = output_path / "stake_historic.csv"

    displacements_export = displacements.drop(
        columns=["annualized_speed"],
        errors="ignore"
    ).copy()

    float_columns = displacements_export.select_dtypes(include="float").columns
    displacements_export[float_columns] = displacements_export[float_columns].round(5)

    if "dt_days" in displacements_export.columns:
        displacements_export["dt_days"] = displacements_export["dt_days"].round().astype("Int64")

    displacements_export.to_csv(
        output_path / "displacements_list.csv",
        index=False,
        float_format="%.5f"
    )

    issues.to_csv(
        output_path / "trajectory_issues.csv",
        index=False
    )

    stakes_export = stake_historic.copy()

    if "dt_days" in stakes_export.columns:
        stakes_export["dt_days"] = stakes_export["dt_days"].round().astype("Int64")

    if "mean_speed_m_per_year" in stakes_export.columns:
        stakes_export["mean_speed_m_per_year"] = stakes_export["mean_speed_m_per_year"].round(2)

    _round_existing_columns(
        stakes_export,
        ["total_dx_m", "total_dy_m"],
        decimals=3,
    )
    _round_existing_columns(
        stakes_export,
        ["total_dz_m", "historic_vx_m_per_day", "historic_vy_m_per_day"],
        decimals=5,
    )

    stakes_export.to_csv(stake_historic_path, index=False)

    campaign_summary.to_csv(
        output_path / "campaign_summary.csv",
        index=False
    )

    predictions_path = output_path / "predictions.csv"
    if prediction is not None and not prediction.empty:
        prediction_export = prediction.copy()
        _round_existing_columns(
            prediction_export,
            ["x", "y", "x_pred", "y_pred", "delta_x", "delta_y"],
            decimals=3,
        )
        prediction_export = prediction_export.drop(
            columns=["vx_est", "vy_est"],
            errors="ignore",
        )

        prediction_export.to_csv(
            predictions_path,
            index=False
        )
    elif predictions_path.exists():
        predictions_path.unlink()

    validation_summary_path = output_path / "validation_summary.csv"
    validation_details_path = output_path / "validation_details.csv"

    if validation_summary is not None and not validation_summary.empty:
        validation_summary_export = validation_summary.copy()
        _round_existing_columns(
            validation_summary_export,
            [
                "mean_abs_err_x_m",
                "mean_abs_err_y_m",
                "mean_err_dist_m",
                "rmse_dist_m",
                "median_err_dist_m",
            ],
            decimals=3,
        )

        validation_summary_export.to_csv(
            validation_summary_path,
            index=False
        )
    elif validation_summary_path.exists():
        validation_summary_path.unlink()

    if validation_details is not None and not validation_details.empty:
        validation_details_export = validation_details.copy()
        _round_existing_columns(
            validation_details_export,
            ["x_start", "y_start", "x_obs", "y_obs", "x_pred", "y_pred"],
            decimals=3,
        )
        _round_existing_columns(
            validation_details_export,
            ["err_x_m", "err_y_m", "err_dist_m"],
            decimals=3,
        )
        validation_details_export = validation_details_export.drop(
            columns=["vx_est", "vy_est"],
            errors="ignore",
        )

        validation_details_export.to_csv(
            validation_details_path,
            index=False
        )
    elif validation_details_path.exists():
        validation_details_path.unlink()

    export_geopackage(
        cleaned_trajectories=cleaned_trajectories,
        stake_historic=stake_historic,
        prediction=prediction,
        validation_details=validation_details,
        output_path=output_path / "results.gpkg",
    )
