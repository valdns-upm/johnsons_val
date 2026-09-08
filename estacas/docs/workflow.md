workflow.md
Excel files for each campaign are placed in data/raw/.
main.py reads the measurements and reconstructs trajectories.
Results are written to output/.
Point velocity exports (X, Y, vx/vy) are produced in output/ and then consumed by kriging/.
