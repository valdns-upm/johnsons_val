#!/bin/bash
# Quick health check for a running (or finished) ElmerIce inversion.
# Run from the inversion/ directory: bash scripts/check_run.sh

set -u
export LC_ALL=C   # avoid comma-as-decimal-separator locales breaking awk/printf

echo "--- Process ---"
PID=$(pgrep -x ElmerSolver | head -1)
if [ -n "$PID" ]; then
    ELAPSED=$(ps -o etime= -p "$PID" | tr -d ' ')
    echo "alive (PID $PID, elapsed $ELAPSED)"
else
    echo "not running"
fi

echo
echo "--- Last file update ---"
if [ -f Cost_steady.dat ]; then
    LAST=$(stat -c %Y Cost_steady.dat)
    NOW=$(date +%s)
    AGO=$(( (NOW - LAST) / 60 ))
    echo "Cost_steady.dat last written ${AGO} min ago"
elif [ -n "$PID" ]; then
    echo "Cost_steady.dat not written yet - still inside the first flow solve, this is normal early on"
    exit 0
else
    echo "Cost_steady.dat not found - no run started here yet"
    exit 0
fi

echo
echo "--- Cost trend (last 5 evaluations) ---"
tail -5 Cost_steady.dat | awk '{printf "%.0f  %.4e\n", $1, $2}'

echo
echo "--- Gradient norm (last value) ---"
tail -1 GradientNormAdjoint_steady.dat 2>/dev/null

echo
echo "--- m1qn3 optimizer iterations completed ---"
grep -c "^ m1qn3: iter" M1QN3_steady.out 2>/dev/null

echo
echo "--- Backtracks in the current/last line search ---"
LAST_ITER_LINE=$(grep -n "^ m1qn3: iter" M1QN3_steady.out 2>/dev/null | tail -1 | cut -d: -f1)
if [ -n "${LAST_ITER_LINE:-}" ]; then
    BACKTRACKS=$(tail -n +"$LAST_ITER_LINE" M1QN3_steady.out | grep -c mlis3)
    echo "$BACKTRACKS"
    if [ "$BACKTRACKS" -gt 10 ]; then
        echo "WARNING: high backtrack count - see docs/run_health_checklist.md"
    fi
else
    echo "n/a"
fi
