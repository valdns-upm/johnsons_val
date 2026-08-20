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
    Validation enabled: True
    Prediction target date: 2026-01-10

Run
    python main.py

Main outputs (outputs/)
    displacements_list.csv
    -> valid displacements between cleaned points

    trajectory_issues.csv
    -> detected issues:
       ONLY_ONE_POINT, DUPLICATE_DATE, OUTLIER

    campaign_summary.csv
    -> number of measurements per stake and campaign

    stake_historic.csv
    -> historical summary and estimated velocity by stake

    predictions.csv
    -> predicted position and prediction status for each stake

    validation_summary.csv
    -> global validation metrics

    validation_details.csv
    -> prediction errors for each validated stake

    results.gpkg
    -> GIS layers for historic trajectories, predictions, unpredicted stakes,
       and validation results

Notes
    Dates are normalized before parsing, including 2-digit years.
    Stakes with fewer than 2 valid segments are not predicted.
    Stakes marked as lost or no longer monitored are also not predicted.

Start execution here
    Need to activate the environment 'estacas'
    source /data/envs/estacas/bin/activate
    (Procedure to simplify later)
