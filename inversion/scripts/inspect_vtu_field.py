"""Print min/max/mean of a point-data field from Elmer .vtu result files.

.vtu files needs to be run with ParaView's own Python interpreter (pvpython), 
not plain python3: grep/cat cannot read them

    pvpython inspect_vtu_field.py

(needs the `pvpython` alias, see ~/.bash_aliases)

Fields available: alpha, Vsx, Vsy, velocity 1/2/3, pressure, others -
running with a wrong field name prints the full list back.
"""
from paraview.simple import XMLUnstructuredGridReader, servermanager

FIELD = "alpha"  # Point-data array name, e.g. alpha, Vsx, velocity 1
FILES = ["Results/johnsons_inv_01_t0019.vtu"]  # .vtu files to inspect, edit as needed


def field_stats(vtu_path, field):
    reader = XMLUnstructuredGridReader(FileName=[vtu_path])
    reader.UpdatePipeline()
    data = servermanager.Fetch(reader)

    pdata = data.GetPointData()
    arr_names = [pdata.GetArrayName(i) for i in range(pdata.GetNumberOfArrays())]
    if field not in arr_names:
        return f"{vtu_path}: field '{field}' not found. Available: {arr_names}"

    arr = pdata.GetArray(field)
    vals = [arr.GetValue(i) for i in range(arr.GetNumberOfTuples())]
    imin, imax = vals.index(min(vals)), vals.index(max(vals))
    pmin, pmax = data.GetPoint(imin), data.GetPoint(imax)
    mean = sum(vals) / len(vals)

    return (
        f"{vtu_path}: n={len(vals)} {field} "
        f"min={min(vals):.4f} (at {pmin[:2]}) "
        f"max={max(vals):.4f} (at {pmax[:2]}) "
        f"mean={mean:.4f}"
    )


if __name__ == "__main__":
    for f in FILES:
        print(field_stats(f, FIELD))
