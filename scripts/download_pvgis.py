"""Download hourly PVGIS series (irradiance + temperature + wind at 10 m)."""
from pathlib import Path

import requests
import yaml

params = yaml.safe_load(open("config/params.yaml"))
lat, lon = params["site"]["latitude"], params["site"]["longitude"]

URL = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"
query = {
    "lat": lat,
    "lon": lon,
    "startyear": 2015,
    "endyear": 2020,
    "pvcalculation": 0,
    "components": 0,
    "outputformat": "csv",
    # check the database names available for Africa in the PVGIS web tool
    # (Hourly data tab) and adjust if the request is refused:
    # "raddatabase": "PVGIS-SARAH3",
}
r = requests.get(URL, params=query, timeout=300)
r.raise_for_status()
Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/raw/pvgis_hourly.csv").write_text(r.text)
print("written data/raw/pvgis_hourly.csv")
