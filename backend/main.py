from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import os
import requests
import anthropic
from dotenv import load_dotenv
from dataclasses import dataclass, asdict

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://weather-project-csi.com",
        "https://www.weather-project-csi.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

claude_client = anthropic.Anthropic(
    api_key=CLAUDE_API_KEY
)


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
    ai_summary: str


@app.get("/")
def root():
    return {"message": "Weather API is running"}


@app.get("/api/zip-cities")
def get_cities_by_zip(zip_code: str):
    try:
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        weather = requests.get(weather_url, params={
            "zip": f"{zip_code},US",
            "appid": OPENWEATHER_API_KEY
        }).json()

        if "coord" not in weather:
            raise HTTPException(status_code=404, detail="Invalid ZIP code")

        lat = weather["coord"]["lat"]
        lon = weather["coord"]["lon"]

        geo_url = "http://api.openweathermap.org/geo/1.0/reverse"
        geo_resp = requests.get(geo_url, params={
            "lat": lat,
            "lon": lon,
            "limit": 5,
            "appid": OPENWEATHER_API_KEY
        }).json()

        cities = list(set([place["name"] for place in geo_resp]))

        return {"cities": cities}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check")
def check():
    return {"status": "ok"}


@app.post("/api/ask")
def ask_ai(data: dict):
    try:
        question = data.get("question")
        context = data.get("context")

        if not question:
            raise HTTPException(status_code=400, detail="No question provided")

        prompt = f"""
        Weather context:
        {context}

        User question:
        {question}

        Answer clearly and briefly.
        """

        claude_response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return {"answer": claude_response.content[0].text}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weather")
def get_weather(query: str, units: str = "imperial"):
    try:
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        geo_resp = requests.get(geo_url, params={
            "q": query,
            "limit": 1,
            "appid": OPENWEATHER_API_KEY
        }).json()

        if not geo_resp:
            raise HTTPException(status_code=404, detail="Location not found")

        lat = geo_resp[0]["lat"]
        lon = geo_resp[0]["lon"]
        name = geo_resp[0]["name"]

        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        weather = requests.get(weather_url, params={
            "lat": lat,
            "lon": lon,
            "units": units,
            "appid": OPENWEATHER_API_KEY
        }).json()

        temperature = weather["main"]["temp"]
        condition = weather["weather"][0]["description"]

        prompt = f"""
        The current weather in {name} is {temperature} degrees with {condition}.
        Give a short, friendly summary and advice for someone going outside.
        """

        claude_response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        ai_summary = claude_response.content[0].text

        response = WeatherResponse(
            location=NormalizedLocation(name, lat, lon),
            current=CurrentConditions(temperature, condition),
            ai_summary=ai_summary
        )

        return asdict(response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
