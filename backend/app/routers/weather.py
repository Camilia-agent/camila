"""Weather proxy backed by Open-Meteo (no API key required).

Docs: https://open-meteo.com/en/docs
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/weather", tags=["weather"])

FORECAST_URL  = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

DEFAULT_LOCATION = {
    "city":     "Hyderabad",
    "country":  "IN",
    "lat":      17.385,
    "lon":      78.4867,
    "timezone": "Asia/Kolkata",
}

# WMO weather interpretation codes → (icon, short condition text)
# https://open-meteo.com/en/docs#weathervariables
WMO = {
    0:  ("☀️", "Clear Sky"),
    1:  ("🌤️", "Mostly Sunny"),
    2:  ("⛅",  "Partly Cloudy"),
    3:  ("☁️", "Overcast"),
    45: ("🌫️", "Foggy"),
    48: ("🌫️", "Depositing Rime Fog"),
    51: ("🌦️", "Light Drizzle"),
    53: ("🌦️", "Drizzle"),
    55: ("🌦️", "Dense Drizzle"),
    56: ("🌧️", "Freezing Drizzle"),
    57: ("🌧️", "Heavy Freezing Drizzle"),
    61: ("🌧️", "Light Rain"),
    63: ("🌧️", "Rain"),
    65: ("🌧️", "Heavy Rain"),
    66: ("🌧️", "Freezing Rain"),
    67: ("🌧️", "Heavy Freezing Rain"),
    71: ("🌨️", "Light Snow"),
    73: ("🌨️", "Snow"),
    75: ("🌨️", "Heavy Snow"),
    77: ("🌨️", "Snow Grains"),
    80: ("🌦️", "Rain Showers"),
    81: ("🌦️", "Rain Showers"),
    82: ("🌧️", "Violent Rain Showers"),
    85: ("🌨️", "Snow Showers"),
    86: ("🌨️", "Heavy Snow Showers"),
    95: ("⛈️", "Thunderstorm"),
    96: ("⛈️", "Thunderstorm w/ Hail"),
    99: ("⛈️", "Severe Thunderstorm"),
}


def _describe(code: int) -> tuple[str, str]:
    return WMO.get(code, ("🌤️", "Unknown"))


def _geocode(query: str) -> dict:
    with httpx.Client(timeout=8.0) as client:
        resp = client.get(GEOCODING_URL, params={"name": query, "count": 1})
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results") or []
    if not results:
        raise HTTPException(status_code=404, detail=f"Location {query!r} not found")

    r = results[0]
    return {
        "city":     r["name"],
        "country":  r.get("country_code", ""),
        "lat":      r["latitude"],
        "lon":      r["longitude"],
        "timezone": r.get("timezone", "UTC"),
    }


@router.get("")
def weather(
    q:   str | None = Query(None, description="City name; geocoded if provided"),
    lat: float | None = None,
    lon: float | None = None,
):
    if q:
        loc = _geocode(q)
    elif lat is not None and lon is not None:
        loc = {
            "city": "Custom", "country": "",
            "lat": lat, "lon": lon, "timezone": "auto",
        }
    else:
        loc = DEFAULT_LOCATION

    params = {
        "latitude":  loc["lat"],
        "longitude": loc["lon"],
        "current":   "temperature_2m,weather_code",
        "daily":     "temperature_2m_max,temperature_2m_min,weather_code",
        "timezone":  loc["timezone"],
        "forecast_days": 6,
    }

    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(FORECAST_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Weather provider error: {exc}") from exc

    current = data["current"]
    daily   = data["daily"]

    cur_icon, cur_cond = _describe(current["weather_code"])
    today_hi = round(daily["temperature_2m_max"][0])
    today_lo = round(daily["temperature_2m_min"][0])

    forecast: list[dict] = []
    for i in range(1, min(6, len(daily["time"]))):
        day_date = datetime.fromisoformat(daily["time"][i]).date()
        icon, _  = _describe(daily["weather_code"][i])
        forecast.append({
            "label": day_date.strftime("%a"),
            "icon":  icon,
            "temp":  f"{round(daily['temperature_2m_max'][i])}°",
        })

    try:
        local_now = datetime.now(ZoneInfo(loc["timezone"]))
    except Exception:
        local_now = datetime.utcnow()

    hour12 = local_now.hour % 12 or 12
    ampm   = "AM" if local_now.hour < 12 else "PM"

    return {
        "location":     f"{loc['city']}, {loc['country']}".strip(", "),
        "localDate":    f"{local_now.strftime('%A')}, {local_now.day} {local_now.strftime('%B')}",
        "localTime":    f"{hour12}:{local_now.minute:02d} {ampm}",
        "localSubLine": f"{local_now.strftime('%A')}, {local_now.day} {local_now.strftime('%B')} · {hour12}:{local_now.minute:02d} {ampm}",
        "current": {
            "temp":      f"{round(current['temperature_2m'])}°",
            "condition": cur_cond,
            "icon":      cur_icon,
            "high":      f"{today_hi}°",
            "low":       f"{today_lo}°",
        },
        "forecast": forecast,
    }
