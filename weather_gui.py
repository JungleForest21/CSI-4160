import tkinter as tk
from tkinter import messagebox
import requests

API_URL = "http://127.0.0.1:8000/weather"

def get_weather():

    location = location_entry.get().strip()

    if location == "":
        messagebox.showerror("Error", "Please enter a ZIP code or city, state.")
        return

    try:

        response = requests.get(f"{API_URL}/{location}")

        if response.status_code != 200:
            messagebox.showerror("Error", "Backend API request failed")
            return

        data = response.json()

        city_name = data["city"]
        region = data["region"]
        country = data["country"]
        forecast_days = data["forecast"]

        forecast_text = ""

        for day in forecast_days:

            date = day["date"]
            tempmax = day["max_temp"]
            tempmin = day["min_temp"]
            condition = day["condition"]

            forecast_text += f"{date} | High: {tempmax}°F | Low: {tempmin}°F | {condition}\n"

        forecast_title.config(text=f"7-Day Forecast for {city_name}, {region}, {country}")
        forecast_label.config(text=forecast_text)

        page1.pack_forget()
        page2.pack(fill="both", expand=True)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Network problem:\n{e}")

def go_back():

    page2.pack_forget()
    page1.pack(fill="both", expand=True)


root = tk.Tk()
root.title("Weather App")
root.geometry("700x400")

root.config(bg="#87CEEB")

# PAGE 1
page1 = tk.Frame(root, bg="#87CEEB")

title_label = tk.Label(page1, text="Weather App", font=("Arial", 20, "bold"))
title_label.pack(pady=20)

instruction_label = tk.Label(page1, text="Enter ZIP code or City, State")
instruction_label.pack(pady=5)

location_entry = tk.Entry(page1, width=30, font=("Arial", 12))
location_entry.pack(pady=10)

go_button = tk.Button(page1, text="Go", width=12, command=get_weather)
go_button.pack(pady=10)

page1.pack(fill="both", expand=True)

# PAGE 2
page2 = tk.Frame(root, bg="#87CEEB")

forecast_title = tk.Label(page2, text="", font=("Arial", 16, "bold"))
forecast_title.pack(pady=20)

forecast_label = tk.Label(page2, text="", font=("Arial", 11), justify="left")
forecast_label.pack(pady=10)

back_button = tk.Button(page2, text="Back", width=12, command=go_back)
back_button.pack(pady=20)

root.mainloop()