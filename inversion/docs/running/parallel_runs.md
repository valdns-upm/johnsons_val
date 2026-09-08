# Running several inversions in parallel

ElmerSolver runs single-threaded: 1 task / 1 thread per run 
(check run.log for "Running one task without MPI");
32 cores and <1GB RAM/run => parallel runs cost nothing extra.

Same directory pattern is used for archived campaign runs (`camp_0609/`,
`camp_1517/`) even when they're run one after another, not in parallel -
it's what keeps a validated run from being overwritten the next time
`johnsons_inversion.sif` is run at the root with different data.

Each run needs its own directory:

    lcurve/1e6/
      johnsons_inversion.sif
      results/
      mesh_Johnson_gmsh_2D_100_front_refined/   # empty, see below

Steps to set one up (copy from the main johnsons_inversion.sif):


1. Fix relative paths in the .sif:
        - Mesh DB, 
        - DEM files, 
        - Kriged velocity
   files are all relative to the run directory, not the repo root.

2. Create the results/ directory.

3. Create an empty dir named exactly like the mesh dir (ex: mesh_Johnson_gmsh_2D_100_front_refined):
        ElmerSolver writes the .result checkpoint there regardless of Mesh DB path; 
        missing dir => run fails.


Launch with tmux (survives closing the terminal/VSCode):
    tmux new-session -d -s myrun -c /path/to/rundir "ElmerSolver johnsons_inversion.sif > run.log 2>&1"


Check on it:
    tmux ls                    # list active runs
    tmux attach -t myrun        # watch live, Ctrl+B D to detach
    tail -f rundir/run.log      # or just tail the log from anywhere

Watch memory with `free -h` if launching many at once - fine at current
mesh size, would matter with a much bigger mesh.
