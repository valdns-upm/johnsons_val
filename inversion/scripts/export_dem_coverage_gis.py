"""Export DEM coverage (valid vs no-data) as a QGIS-readable layer."""

import numpy as np
import geopandas as gpd
from shapely.geometry import Point

CRS = "EPSG:32720"
NODATA = -9999.0

# The two mesh nodes where alpha diverged, both landing on Zs=0.0
PROBLEM_NODES = [
    ("max-node", 635230.1, 3049297.9),
    ("min-node", 635469.74672, 3049614.81862),
]


def dem_layer(path, label):
    arr = np.loadtxt(path)
    valid = arr[:, 2] != NODATA
    gdf = gpd.GeoDataFrame(
        {"elevation": arr[:, 2], "valid": valid},
        geometry=[Point(x, y) for x, y in arr[:, :2]],
        crs=CRS,
    )
    return gdf


def main():
    surf = dem_layer("mesh/DEM_Johnsons_surf.dat", "surface")
    bed = dem_layer("mesh/DEM_Johnsons_bed.dat", "bed")
    problem = gpd.GeoDataFrame(
        {"name": [n for n, _, _ in PROBLEM_NODES]},
        geometry=[Point(x, y) for _, x, y in PROBLEM_NODES],
        crs=CRS,
    )

    out = "results/Johnsons_dem_coverage.gpkg"
    surf.to_file(out, layer="surface_dem", driver="GPKG")
    bed.to_file(out, layer="bed_dem", driver="GPKG")
    problem.to_file(out, layer="problem_nodes", driver="GPKG")
    print(f"Wrote {out} (layers: surface_dem, bed_dem, problem_nodes)")


if __name__ == "__main__":
    main()
