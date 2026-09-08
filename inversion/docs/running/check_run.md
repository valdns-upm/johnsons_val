# Reading check_run.sh output

check_run.sh only prints raw numbers (process status, file ages, cost
values) - it doesn't judge them. This file says what counts as normal vs.
a problem.

Process
    not running + no recent update = run finished or crashed, check run_full.log
    alive = ok

Last file update
    time since Cost_steady.dat was last written (one write per cost/gradient eval)
    >15-20 min while alive = probably stuck in one very long flow solve

Cost trend
    should decrease then flatten
    flat for 10+ evals while iter count stays put = optimizer stuck, see ../lambda/line_search_diagnosis.md
    jump of several orders of magnitude = numerical divergence

Gradient norm
    should trend down
    flat/noisy while cost is also flat = consistent with a stuck line search, not new

m1qn3 iterations vs Cost_steady.dat row count
    big gap (e.g. 13 iterations, 90+ evals) = most of the budget burned on failed
    line search attempts, not real progress

Backtracks (last line search)
    1-4   normal
    5-10  watch it
    >10   same signature as the known stall - check alpha with inspect_vtu_field.py,
          look for extreme values (outside ~[-3,+3]) on a couple of nodes
