from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

API_KEY = "541e5a0ca12546ae99205719261203"

@app.get("/weather/{location}")
def get_weather(location: str):

    url = "http://api.weatherapi.com/v1/forecast.json"

    params = {
        "key": API_KEY,
        "q": location,
        "days": 7
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Weather API request failed")

        data = response.json()

        result = {
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "forecast": []
        }

        for day in data["forecast"]["forecastday"]:
            result["forecast"].append({
                "date": day["date"],
                "max_temp": day["day"]["maxtemp_f"],
                "min_temp": day["day"]["mintemp_f"],
                "condition": day["day"]["condition"]["text"]
            })

        return result

    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Network error contacting WeatherAPI")