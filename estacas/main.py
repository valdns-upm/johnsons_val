from src.pipeline import run_pipeline

# Role:
# Entry point for a manual, single-campaign run. For running several
# campaigns at once (estacas -> kriging -> inversion), see ../pipeline/.

# Set to False to skip position prediction. target_date below is currently in
# the past relative to today, and data/validation/ already holds a real
# campaign close to that date -- running it now would be a backtest against
# known data, not a forecast. Set True (with a future target_date) for a
# real forward prediction.
run_prediction = False

run_validation = False    # Set to False to skip validation step, True to run it

# Date the 3-year smoothed velocity window ends on, e.g. "2008-12-31".
# None = use the most recent measurement in the dataset.
smoothed_velocity_target_date = None

run_pipeline(
    data_paths="data/raw/",
    output_dir="output",
    validation_path="data/validation/",
    run_validation=run_validation,
    run_prediction=run_prediction,
    prediction_target_date="2026-01-10",  # Change target date for prediction if needed
    smoothed_velocity_target_date=smoothed_velocity_target_date,
)
