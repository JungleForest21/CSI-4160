from fastapi import FastAPI
import requests
from dataclasses import dataclass
from typing import List

app = FastAPI()

API_KEY = "YOUR_OPENWEATHER_KEY"


# https://api.weather.gov/ (myweatherapp.com)

# https://openweathermap.org/api/one-call-3?collection=one_call_api_3.0&collection=one_call_api_3.0#current



# ---------- Data Structures ----------

@dataclass
class NormalizedLocation:
    name: str
    latitude: float
    longitude: float

@dataclass
class CurrentConditions:
    temperature: float
    condition: str

@dataclass
class WeatherResponse:
    location: NormalizedLocation
    current: CurrentConditions


# ---------- API Endpoint ----------

@app.get("/api/weather")
def get_weather(query: str, units: str = "imperial"):
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    geo_resp = requests.get(geo_url, params={
        "q": query,
        "limit": 1,
        "appid": API_KEY
    }).json()

    lat = geo_resp[0]["lat"]
    lon = geo_resp[0]["lon"]
    name = geo_resp[0]["name"]

    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    weather = requests.get(weather_url, params={
        "lat": lat,
        "lon": lon,
        "units": units,
        "appid": API_KEY
    }).json()

    response = WeatherResponse(
        location=NormalizedLocation(name, lat, lon),
        current=CurrentConditions(
            temperature=weather["main"]["temp"],
            condition=weather["weather"][0]["description"]
        )
    )

    return response