architecture.md

Folders
    data/raw/           campaign Excel files, one per campaign
    data/validation/    (optional) held-out campaign, used only if run_validation=True
    output/             all generated files
    src/                pipeline code
    docs/               this file, workflow.md, data.md
    tests/              pytest, targeted at edge-case logic (dates, windows, exclusions)

src/ modules
    io.py
        Load Excel files (sheets "Estacas Hurd", "Estacas Johnsons"),
        normalize dates (incl. 2-digit years), clean/rename columns,
        infer campaign+phase from file name, infer glacier (hurd/johnson)
        from stake_id prefix (EH/EJ). Also builds monitoring metadata:
        per-stake "lost"/"new" flags from the GPS comment column.

    trajectory.py
        Group measurements by stake into trajectories, sort by date.
        Walk each trajectory and drop points that imply a segment speed
        above max_speed (5 m/day) -> issue OUTLIER. Also flags
        ONLY_ONE_POINT and DUPLICATE_DATE. Computes dx/dy/dz and speed
        per remaining segment.

    analysis.py
        estimate_velocity_components: duration-weighted vx/vy from a set
        of segments (used by prediction, validation and smoothing alike).
        compute_stake_historic: one summary row per stake (n_points,
        valid_segments, mean speed, outlier flag).
        compute_campaign_summary: per-stake data coverage per campaign.
        compute_prediction: linear estimate forward from last known
        position to target_date, skipped for stakes marked lost/not-monitored/
        single-measurement (build_prediction_status).
        aggregate_window_velocity: one velocity point per stake, averaged
        over the window_years preceding target_date. Used for the
        smoothed kriging export.

    validation.py
        evaluate_prediction_with_validation: predicts each stake's
        position at the date of its first validation-campaign measurement
        from data/raw/ only, compares to the real position, reports RMSE.

    pipeline.py
        export_results: writes all CSVs (displacements, issues,
        stake_historic, campaign_summary, predictions, validation) and
        calls geospatial.export_geopackage.
        export_kriging_inputs: one row per valid Johnsons segment ->
        johnsons_vx.dat / johnsons_vy.dat / johnsons_velocity_metadata.csv.
        export_smoothed_kriging_inputs: one row per stake, using
        aggregate_window_velocity -> johnsons_vx_{year}_smooth.dat and
        matching vy/metadata files. Both consumed by ../kriging/.

    geospatial.py
        Builds the GeoPackage layers (historic trajectories, predictions,
        unpredicted stakes, validation error lines/points) and writes
        output/results.gpkg. Needs geopandas + shapely, imported lazily
        so the rest of the pipeline runs without them installed.

main.py
    Entry point, runs the steps in order below. Toggles and dates to
    edit are at the top of the file (see README.md).

Call order
    load_multiple_files, load_monitoring_metadata      (io.py)
    build_trajectories, compute_displacements           (trajectory.py)
    compute_stake_historic, compute_campaign_summary     (analysis.py)
    compute_prediction                    [if run_prediction]
    evaluate_prediction_with_validation   [if run_validation]
    export_results -> export_geopackage    (pipeline.py, geospatial.py)
    export_kriging_inputs
    export_smoothed_kriging_inputs

Run
    source /data/johnsons_val/.venv/bin/activate
    python main.py
