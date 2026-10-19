"""Plan B: NASA POWER hourly point data (wind is given at 50 m, not 100 m)."""
from pathlib import Path

import requests
import yaml

params = yaml.safe_load(open("config/params.yaml"))
lat, lon = params["site"]["latitude"], params["site"]["longitude"]

URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
query = {
    "parameters": "ALLSKY_SFC_SW_DWN,T2M,WS50M",
    "community": "RE",
    "longitude": lon,
    "latitude": lat,
    "start": "20200101",
    "end": "20201231",
    "format": "CSV",
}
r = requests.get(URL, params=query, timeout=300)
r.raise_for_status()
Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/raw/nasa_power_2020.csv").write_text(r.text)
print("written data/raw/nasa_power_2020.csv")
