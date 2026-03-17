import tkinter as tk
from tkinter import messagebox
import requests
import threading
from fastapi import FastAPI, HTTPException
import uvicorn

API_KEY = "541e5a0ca12546ae99205719261203"

app = FastAPI()

# ---------- FASTAPI BACKEND ----------

@app.get("/weather/{location}")
def get_weather(location: str):

    url = "http://api.weatherapi.com/v1/forecast.json"

    params = {
        "key": API_KEY,
        "q": location,
        "days": 7
    }

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


# ---------- TKINTER FRONTEND ----------

API_URL = "http://127.0.0.1:8000/weather"

def get_weather_gui():

    location = location_entry.get().strip()

    if location == "":
        messagebox.showerror("Error", "Please enter a ZIP code or city, state.")
        return

    try:

        response = requests.get(f"{API_URL}/{location}")

        if response.status_code != 200:
            messagebox.showerror("Error", "API request failed")
            return

        data = response.json()

        city = data["city"]
        region = data["region"]
        country = data["country"]

        forecast_text = ""

        for day in data["forecast"]:

            forecast_text += (
                f"{day['date']} | "
                f"High: {day['max_temp']}°F | "
                f"Low: {day['min_temp']}°F | "
                f"{day['condition']}\n"
            )

        forecast_title.config(text=f"7-Day Forecast for {city}, {region}, {country}")
        forecast_label.config(text=forecast_text)

        page1.pack_forget()
        page2.pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def go_back():
    page2.pack_forget()
    page1.pack(fill="both", expand=True)


# ---------- START FASTAPI SERVER ----------

def start_api():
    uvicorn.run(app, host="127.0.0.1", port=8000)


api_thread = threading.Thread(target=start_api, daemon=True)
api_thread.start()


# ---------- TKINTER UI ----------

root = tk.Tk()
root.title("Weather App")
root.geometry("700x400")

root.config(bg="#87CEEB")

page1 = tk.Frame(root, bg="#87CEEB")

title_label = tk.Label(page1, text="Weather App", font=("Arial", 20, "bold"))
title_label.pack(pady=20)

instruction_label = tk.Label(page1, text="Enter ZIP code or City, State")
instruction_label.pack(pady=5)

location_entry = tk.Entry(page1, width=30, font=("Arial", 12))
location_entry.pack(pady=10)

go_button = tk.Button(page1, text="Go", width=12, command=get_weather_gui)
go_button.pack(pady=10)

page1.pack(fill="both", expand=True)

page2 = tk.Frame(root, bg="#87CEEB")

forecast_title = tk.Label(page2, text="", font=("Arial", 16, "bold"))
forecast_title.pack(pady=20)

forecast_label = tk.Label(page2, text="", font=("Arial", 11), justify="left")
forecast_label.pack(pady=10)

back_button = tk.Button(page2, text="Back", width=12, command=go_back)
back_button.pack(pady=20)

root.mainloop()