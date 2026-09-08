Inputs: vx, vy exports produced by ESTACAS + interpolation grid (Elmer/Ice mesh nodes).
Processing: ordinary kriging.
Outputs: interpolated velocity fields usable by Elmer/Ice.

---

Inputs:
- ../estacas/output/johnsons_vx*.dat: X, Y, X velocity (produced by ESTACAS -
  plain (johnsons_vx.dat) or smoothed (johnsons_vx_{year}_smooth.dat))
- ../estacas/output/johnsons_vy*.dat: same, Y velocity
- input/johnsons_mesh_grid.dat: interpolation grid, X, Y of the target Elmer/Ice mesh nodes (copied from the mesh, not an ESTACAS product)

Kriging outputs (output/):
- johnsons_vx_kriged*.dat, johnsons_vy_kriged*.dat: X Y value (Elmer/Ice format, plain text)
- johnsons_velocity_kriged*.gpkg: same points as a GIS layer (GeoPackage, EPSG:32720),
  attributes vx_m_per_year, vy_m_per_year, speed_m_per_year, direction_deg (azimuth, 0=North)

Headless execution, e.g. for the 2017 smoothed export:
    python ClsMain.py --headless \
      --semi ../estacas/output/johnsons_vx_2017_smooth.dat \
      --krige ../estacas/output/johnsons_vx_2017_smooth.dat \
      --grid input/johnsons_mesh_grid.dat \
      --output output/johnsons_vx_kriged_2017_smooth.dat
    (same for vy; drop the "_2017_smooth" suffix for the plain, non-smoothed export)

    The {year} tag is ESTACAS's target_date.year - check it matches the
    last full year the window actually represents. It won't if the most
    recent measurement landed in January instead of the usual December
    (e.g. target_date 2018-01-04 -> tag says 2018, but the window's last
    full year is 2017) - rename the exports by hand if so.

    python export_gis.py   # paths hardcoded at top of the script

Files in input/ and output/ are local and not tracked by Git.
