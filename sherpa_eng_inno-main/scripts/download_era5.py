"""Download ERA5 hourly data for a small box around the site, one file per year.

Prerequisites: CDS account, licence accepted on the dataset page, ~/.cdsapirc created.
If the request format is rejected, open the dataset page, tick the variables,
click "Show API request" and copy the exact dictionary.
"""
from pathlib import Path

import cdsapi
import yaml

params = yaml.safe_load(open("config/params.yaml"))
lat, lon = params["site"]["latitude"], params["site"]["longitude"]
area = [lat + 0.35, lon - 0.35, lat - 0.35, lon + 0.35]  # North, West, South, East

client = cdsapi.Client()
Path("data/raw").mkdir(parents=True, exist_ok=True)

for year in range(2019, 2024):
    target = f"data/raw/era5_{year}.nc"
    if Path(target).exists():
        continue
    client.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "variable": [
                "100m_u_component_of_wind",
                "100m_v_component_of_wind",
                "2m_temperature",
                "surface_solar_radiation_downwards",
            ],
            "year": str(year),
            "month": [f"{m:02d}" for m in range(1, 13)],
            "day": [f"{d:02d}" for d in range(1, 32)],
            "time": [f"{h:02d}:00" for h in range(24)],
            "area": area,
            "data_format": "netcdf",
        },
        target,
    )
    print("downloaded", target)
