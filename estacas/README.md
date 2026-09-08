README - Estacas

Objective
    Read Excel files of stake measurements,
    compute historical displacements, predict stake positions at a target date,
    and optionally validate predictions with a later campaign.

Input data
    Excel files in:
        data/raw/
        data/validation/   (optional)

    Sheets expected:
        Estacas Hurd
        Estacas Johnsons

    Columns used:
        Id. estaca
        Fecha
        X (E-UTM)
        Y (N-UTM)
        Z (WGS84)

Workflow
    Loading of all Excel files in data/raw/
    Date normalization + missing-value cleaning
    Trajectory reconstruction, by stake
    Removal of abnormal points
    Displacement calculation between valid points
    Historical velocity estimation
    Linear position prediction to a target date
    (Optional validation with files in data/validation/)
    Export of CSV results and GeoPackage layers

Current settings to change in main.py
    Validation enabled (run_validation): False
    Prediction enabled (run_prediction): False
        (target_date is currently in the past relative to today, and
        data/validation/ already holds a real campaign close to that date;
        running it now would be a backtest, not a forecast. Set True with a
        future target_date for a real forward prediction.)
    Prediction target date: 2026-01-10
    Smoothed velocity window end date: smoothed_velocity_target_date
        (None = most recent measurement; set e.g. "2008-12-31" to get
        the smoothed velocity for a specific past window instead)

Run
    python main.py

Main outputs (output/)
    displacements_list.csv
    -> valid displacements between cleaned points

    trajectory_issues.csv
    -> detected issues:
       ONLY_ONE_POINT, DUPLICATE_DATE, OUTLIER

    campaign_summary.csv
    -> number of measurements per stake and campaign

    stake_historic.csv
    -> historical summary and estimated velocity by stake

    predictions.csv (only if run_prediction=True)
    -> predicted position and prediction status for each stake

    validation_summary.csv (only if run_validation=True)
    -> global validation metrics

    validation_details.csv (only if run_validation=True)
    -> prediction errors for each validated stake

    results.gpkg
    -> GIS layer for historic trajectories (always produced);
       predictions and unpredicted-stakes layers (if run_prediction=True)
       and validation-result layers (if run_validation=True) are added
       on top when enabled

    johnsons_vx.dat, johnsons_vy.dat, johnsons_velocity_metadata.csv
    -> per-segment velocity points (all valid Johnsons segments), consumed by kriging/

    johnsons_vx_{year}_smooth.dat, johnsons_vy_{year}_smooth.dat,
    johnsons_velocity_metadata_{year}_smooth.csv
    -> one smoothed velocity point per stake, averaged over the 3 years
       preceding the most recent measurement ({year} in the file name).
       Stakes with less than 3 years of history are excluded rather than
       averaged over a partial window. Not produced if no stake yet has
       3 years of history.

Notes
    Dates are normalized before parsing, including 2-digit years.
    Stakes with fewer than 2 valid segments are not predicted.
    Stakes marked as lost or no longer monitored are also not predicted.

Start execution here
    Need to activate the johnsons_val environment
    source /data/johnsons_val/.venv/bin/activate
