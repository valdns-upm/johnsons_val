"""Combine the kriged vx/vy .dat components into one GIS-readable point layer.

Needs geopandas and shapely - use the project venv (/data/johnsons_val/.venv).

Usage:
    python export_gis.py
"""
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

VX_PATH = "output/johnsons_vx_kriged.dat"
VY_PATH = "output/johnsons_vy_kriged.dat"
OUTPUT_PATH = "output/johnsons_velocity_kriged.gpkg"
CRS = "EPSG:32720"


def build_velocity_layer(vx_path, vy_path, crs=CRS):
    vx = np.loadtxt(vx_path)
    vy = np.loadtxt(vy_path)

    if vx.shape[0] != vy.shape[0]:
        raise ValueError(
            f"vx ({vx_path}, {vx.shape[0]} points) and vy ({vy_path}, {vy.shape[0]} "
            "points) do not have the same number of points; re-run kriging with the "
            "same grid for both components."
        )
    if not np.allclose(vx[:, :2], vy[:, :2], atol=1.0):
        raise ValueError(
            f"vx and vy were kriged onto different grids (coordinates in {vx_path} "
            f"and {vy_path} do not match); re-run kriging with the same grid for both."
        )

    x, y = vx[:, 0], vx[:, 1]
    vx_val, vy_val = vx[:, 2], vy[:, 2]
    speed = np.hypot(vx_val, vy_val)
    # Azimuth convention: 0 deg = North, 90 deg = East.
    direction = np.degrees(np.arctan2(vx_val, vy_val)) % 360.0

    gdf = gpd.GeoDataFrame(
        {
            "vx_m_per_year": vx_val,
            "vy_m_per_year": vy_val,
            "speed_m_per_year": speed,
            "direction_deg": direction,
        },
        geometry=[Point(xi, yi) for xi, yi in zip(x, y)],
        crs=crs,
    )
    return gdf


if __name__ == "__main__":
    gdf = build_velocity_layer(VX_PATH, VY_PATH)
    gdf.to_file(OUTPUT_PATH, layer="velocity", driver="GPKG")
    print(f"Wrote {len(gdf)} points to {OUTPUT_PATH}")
