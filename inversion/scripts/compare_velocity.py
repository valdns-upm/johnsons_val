"""Extract observed vs modeled surface velocity from a .vtu snapshot.

Surface velocity only: writes vsx/vsy (observed, from kriging) alongside
velocity 1/2 (modeled, from the Stokes solve), one point per (x,y) -
see docs/results/<campaign>/velocity_comparison.md.

Run from the campaign folder (e.g. camp_0609/) with pvpython (not plain
python3):
    pvpython ../scripts/compare_velocity.py
"""
from paraview.simple import XMLUnstructuredGridReader, servermanager

VTU_FILE = "results/johnsons_inv_01_t0100.vtu"  # edit as needed
OUTPUT_FILE = "../docs/results/0609/velocity_comparison.dat"  # edit per campaign


def main():
    reader = XMLUnstructuredGridReader(FileName=[VTU_FILE])
    reader.UpdatePipeline()
    data = servermanager.Fetch(reader)
    pdata = data.GetPointData()
    vsx = pdata.GetArray("vsx")
    vsy = pdata.GetArray("vsy")
    vel = pdata.GetArray("velocity")

    top = {}
    for i in range(data.GetNumberOfPoints()):
        p = data.GetPoint(i)
        key = (round(p[0], 1), round(p[1], 1))
        if key not in top or p[2] > top[key][0]:
            top[key] = (p[2], i)

    with open(OUTPUT_FILE, "w") as f:
        f.write("x y vsx_obs vsy_obs v1_mod v2_mod\n")
        for (x, y), (z, i) in top.items():
            v = vel.GetTuple(i)
            f.write(f"{x} {y} {vsx.GetValue(i)} {vsy.GetValue(i)} {v[0]} {v[1]}\n")
    print(f"Wrote {len(top)} surface points to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
