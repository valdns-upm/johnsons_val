from pathlib import Path

import pandas as pd

from src.geospatial import export_geopackage


def export_kriging_inputs(
    displacements,
    output_dir="outputs/kriging",
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

    scale = {"m_per_day": 1.0, "m_per_year": 365.0, "m_per_second": 1.0 / 86400.0}
    if velocity_unit not in scale:
        raise ValueError(f"Unsupported velocity unit: {velocity_unit}")

    data["vx"] = data["dx"] / data["dt_days"] * scale[velocity_unit]
    data["vy"] = data["dy"] / data["dt_days"] * scale[velocity_unit]
    columns = ["x", "y"]
    data[columns + ["vx"]].to_csv(
        output_path / "Johnsons_vx.dat", sep="\t", index=False, header=False,
        float_format="%.8g"
    )
    data[columns + ["vy"]].to_csv(
        output_path / "Johnsons_vy.dat", sep="\t", index=False, header=False,
        float_format="%.8g"
    )

    # Keep a CSV with stake/date provenance for traceability.
    data[["stake_id", "date_start", "date_end", "x", "y", "vx", "vy"]].to_csv(
        output_path / "Johnsons_velocity_metadata.csv", index=False
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
    prediction,
    validation_summary=None,
    validation_details=None,
):
    stake_historic_path = Path("outputs/stake_historic.csv")

    displacements_export = displacements.drop(
        columns=["annualized_speed"],
        errors="ignore"
    ).copy()

    float_columns = displacements_export.select_dtypes(include="float").columns
    displacements_export[float_columns] = displacements_export[float_columns].round(5)

    if "dt_days" in displacements_export.columns:
        displacements_export["dt_days"] = displacements_export["dt_days"].round().astype("Int64")

    displacements_export.to_csv(
        "outputs/displacements_list.csv",
        index=False,
        float_format="%.5f"
    )

    issues.to_csv(
        "outputs/trajectory_issues.csv",
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
        "outputs/campaign_summary.csv",
        index=False
    )

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
        "outputs/predictions.csv",
        index=False
    )

    validation_summary_path = Path("outputs/validation_summary.csv")
    validation_details_path = Path("outputs/validation_details.csv")

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
    )
