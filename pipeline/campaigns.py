# Registry of processed GPS campaigns: tag -> red_global source folders
# (phase a). Tag = the full calendar years the segments represent, picked
# by hand, not derived from the folder names - see
# estacas/data/camp_<tag>/ (staged raw files) and inversion/camp_<tag>/
# (matching inversion run) for campaigns already run.
#
# A window of N years needs N+1 consecutive campXXYYa folders: the extra
# one only provides the measurement date that closes the last segment,
# it isn't itself part of the window.

from pathlib import Path

RED_GLOBAL_DIR = Path(__file__).resolve().parent.parent / "estacas" / "data" / "red_global"

CAMPAIGNS = {
    "1517": ["camp1415a", "camp1516a", "camp1617a", "camp1718a"],
    "2224": ["camp2122a", "camp2223a", "camp2324a", "camp2425a"],
    # Confirmed against estacas/data/raw + the smoothed export window
    # (2006-12-01 to 2009-12-03, 3 segments): the 3rd segment (08-09) only
    # closes once camp0910a's measurement date is loaded, so it's needed
    # even though it's not part of the "0709" tag itself.
    "0709": ["camp0607a", "camp0708a", "camp0809a", "camp0910a"],
}


def source_dirs(tag):
    return [RED_GLOBAL_DIR / name for name in CAMPAIGNS[tag]]
