"""Generate GeoJSON cloud cover map from ECMWF IFS via Open-Meteo.

Queries cloud cover at a 6x6 grid over the Bay Area, scrapes live
Stanford weather station data, and generates GeoJSON with cloud
density polygons + station markers.

Uses ECMWF IFS 0.25 (9km) for cloud grid.
Stanford weather stations update every 15 minutes.

Outputs GeoJSON to stdout.
"""
import json
import re
import sys
import urllib.request
from datetime import datetime

# Bay Area bounding box for cloud cover grid
GRID_LAT_MIN = 37.25
GRID_LAT_MAX = 37.65
GRID_LON_MIN = -122.55
GRID_LON_MAX = -121.95
GRID_ROWS = 6
GRID_COLS = 6

# General Palo Alto center (not exact home)
HOME_LAT = 37.4419
HOME_LON = -122.1430

# METAR stations
METAR_STATIONS = [
    {"name": "KPAO", "label": "Palo Alto Airport", "lat": 37.461, "lon": -122.115, "color": "#2196F3"},
    {"name": "KNUQ", "label": "Moffett Field (NASA)", "lat": 37.4161, "lon": -122.0496, "color": "#2196F3"},
    {"name": "KSQL", "label": "San Carlos Airport", "lat": 37.5122, "lon": -122.2508, "color": "#2196F3"},
    {"name": "KSFO", "label": "San Francisco Intl", "lat": 37.6213, "lon": -122.3750, "color": "#9C27B0"},
    {"name": "KSJC", "label": "San Jose Intl", "lat": 37.3626, "lon": -121.9289, "color": "#9C27B0"},
]


def fetch_cloud_grid():
    """Fetch cloud cover at grid points from Open-Meteo ECMWF IFS."""
    lat_step = (GRID_LAT_MAX - GRID_LAT_MIN) / GRID_ROWS
    lon_step = (GRID_LON_MAX - GRID_LON_MIN) / GRID_COLS

    grid_data = []
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            lat = GRID_LAT_MIN + (r + 0.5) * lat_step
            lon = GRID_LON_MIN + (c + 0.5) * lon_step
            grid_data.append({"lat": lat, "lon": lon, "row": r, "col": c})

    lats = ",".join(f"{p['lat']:.4f}" for p in grid_data)
    lons = ",".join(f"{p['lon']:.4f}" for p in grid_data)

    url = (
        f"https://api.open-meteo.com/v1/ecmwf?"
        f"latitude={lats}&longitude={lons}"
        f"&hourly=cloud_cover"
        f"&models=ecmwf_ifs025"
        f"&timezone=America/Los_Angeles"
        f"&forecast_days=1"
    )

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"Warning: cloud cover fetch failed: {e}", file=sys.stderr)
        return grid_data

    now = datetime.now()
    results = data if isinstance(data, list) else [data]

    for i, point in enumerate(grid_data):
        if i >= len(results):
            point["cloud_cover"] = 0
            continue
        hourly = results[i].get("hourly", {})
        times = hourly.get("time", [])
        cc = hourly.get("cloud_cover", [])
        hour_idx = 0
        for j, t in enumerate(times):
            if datetime.strptime(t, "%Y-%m-%dT%H:%M") >= now:
                hour_idx = max(0, j - 1)
                break
        val = cc[hour_idx] if hour_idx < len(cc) else None
        point["cloud_cover"] = val if val is not None else 0

    return grid_data


def fetch_stanford_weather():
    """Scrape live data from Stanford weather stations (updates every 15 min)."""
    url = "https://stanford.westernweathergroup.com/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Warning: Stanford weather fetch failed: {e}", file=sys.stderr)
        return None

    # Split HTML by station sections and parse each
    met_idx = html.find("Met Tower")
    rwc_idx = html.find("Redwood City")
    if met_idx < 0:
        return None

    met_html = html[met_idx:rwc_idx] if rwc_idx > met_idx else html[met_idx:]
    rwc_html = html[rwc_idx:] if rwc_idx > 0 else ""

    def parse_rows(section):
        d = {}
        for label, val in re.findall(r'<th>([^<]+)</th>\s*<td[^>]*>\s*([\d.]+)', section):
            d[label.strip()] = val
        return d

    met = parse_rows(met_html)
    rwc = parse_rows(rwc_html) if rwc_html else {}

    # Parse timestamp
    ts_match = re.search(r'(\d+/\d+/\d+\s+\d+:\d+\s*[AP]M)', html)
    timestamp = ts_match.group(1) if ts_match else ""

    return {
        "met_tower": {
            "temp": met.get("Temp", "?"),
            "rh": met.get("RH", "?"),
            "wind": met.get("Wind Spd", "?"),
            "gust": met.get("Wind Gust", "?"),
            "aqi": met.get("NowCast AQI Value", "?"),
            "precip_24h": met.get("Precip 24Hr", "?"),
            "season_precip": met.get("Season Precip", "?"),
        },
        "redwood_city": {
            "temp": rwc.get("Temp", "?"),
            "rh": rwc.get("RH", "?"),
            "wind": rwc.get("Wind Spd", "?"),
            "gust": rwc.get("Wind Gust", "?"),
            "aqi": rwc.get("NowCast AQI Value", "?"),
            "precip_24h": rwc.get("Precip 24Hr", "?"),
            "season_precip": rwc.get("Season Precip", "?"),
        },
        "timestamp": timestamp,
    }


def build_geojson(grid_data, stanford):
    """Build GeoJSON FeatureCollection."""
    lat_step = (GRID_LAT_MAX - GRID_LAT_MIN) / GRID_ROWS
    lon_step = (GRID_LON_MAX - GRID_LON_MIN) / GRID_COLS
    features = []

    # Cloud cover grid polygons
    for point in grid_data:
        cc = point.get("cloud_cover", 0) or 0
        if cc < 5:
            continue
        lat = point["lat"]
        lon = point["lon"]
        half_lat = lat_step / 2
        half_lon = lon_step / 2
        opacity = round(0.03 + (cc / 100) * 0.42, 2)
        if cc >= 80:
            fill = "#9E9E9E"
        elif cc >= 50:
            fill = "#BDBDBD"
        else:
            fill = "#E0E0E0"
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [round(lon - half_lon, 5), round(lat - half_lat, 5)],
                    [round(lon + half_lon, 5), round(lat - half_lat, 5)],
                    [round(lon + half_lon, 5), round(lat + half_lat, 5)],
                    [round(lon - half_lon, 5), round(lat + half_lat, 5)],
                    [round(lon - half_lon, 5), round(lat - half_lat, 5)],
                ]]
            },
            "properties": {
                "stroke": fill,
                "stroke-width": 0,
                "stroke-opacity": 0,
                "fill": fill,
                "fill-opacity": opacity,
                "title": f"{cc}% cloud cover",
                "description": f"ECMWF IFS 0.25 / {lat:.2f}N {abs(lon):.2f}W"
            }
        })

    # Stanford Met Tower (live, 15-min updates)
    if stanford:
        mt = stanford["met_tower"]
        ts = stanford["timestamp"]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-122.1720, 37.4275]},
            "properties": {
                "marker-color": "#8B0000",
                "marker-size": "large",
                "marker-symbol": "college",
                "title": f"Stanford Met Tower - {mt['temp']}F",
                "description": (
                    f"RH {mt['rh']}% / Wind {mt['wind']} mph "
                    f"(gust {mt['gust']}) / AQI {mt['aqi']} / "
                    f"Rain 24h {mt['precip_24h']}in / "
                    f"Season {mt['season_precip']}in / {ts}"
                )
            }
        })

        rc = stanford["redwood_city"]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-122.2150, 37.4850]},
            "properties": {
                "marker-color": "#8B0000",
                "marker-size": "medium",
                "marker-symbol": "college",
                "title": f"Stanford Redwood City - {rc['temp']}F",
                "description": (
                    f"RH {rc['rh']}% / Wind {rc['wind']} mph "
                    f"(gust {rc['gust']}) / AQI {rc['aqi']} / "
                    f"Rain 24h {rc['precip_24h']}in / "
                    f"Season {rc['season_precip']}in / {ts}"
                )
            }
        })

    # Palo Alto marker
    features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [HOME_LON, HOME_LAT]},
        "properties": {
            "marker-color": "#ff4444",
            "marker-size": "large",
            "marker-symbol": "star",
            "title": "Palo Alto",
            "description": "ECMWF IFS forecast point"
        }
    })

    # METAR stations
    for s in METAR_STATIONS:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [s["lon"], s["lat"]]},
            "properties": {
                "marker-color": s["color"],
                "marker-size": "medium",
                "marker-symbol": "airport",
                "title": f"{s['name']} - {s['label']}",
                "description": "METAR station / surface observations"
            }
        })

    # Forecast grid outline
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [GRID_LON_MIN, GRID_LAT_MIN],
                [GRID_LON_MAX, GRID_LAT_MIN],
                [GRID_LON_MAX, GRID_LAT_MAX],
                [GRID_LON_MIN, GRID_LAT_MAX],
                [GRID_LON_MIN, GRID_LAT_MIN],
            ]]
        },
        "properties": {
            "stroke": "#ff4444",
            "stroke-width": 1,
            "stroke-opacity": 0.3,
            "fill": "#ff4444",
            "fill-opacity": 0.02,
            "title": "ECMWF IFS Grid",
            "description": "25km resolution / forecast area"
        }
    })

    return {"type": "FeatureCollection", "features": features}


def main():
    grid = fetch_cloud_grid()
    stanford = fetch_stanford_weather()
    geojson = build_geojson(grid, stanford)
    print(json.dumps(geojson, indent=2))


if __name__ == "__main__":
    main()
