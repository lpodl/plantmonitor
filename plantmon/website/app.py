from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from io import BytesIO
import base64
import pandas as pd
import os
from datetime import datetime
import random

app = Flask(__name__)

def generate_dummy_data(num_records=10):
    dummy_data = []
    for _ in range(num_records):
        record = {
            "Timestamp": datetime.now().isoformat(),
            "Temperature (°C)": round(random.uniform(15.0, 30.0), 2),
            "Humidity (%)": round(random.uniform(30.0, 70.0), 2)
        }
        dummy_data.append(record)
    return pd.DataFrame(dummy_data)

def plot(df):
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["Timestamp"], df["Temperature (°C)"], color="#b25c5c", linestyle="-")
    ax.set(xlabel="Time", ylabel="Temperature (°C)")
    ax.set_ylim(15, 35)
    ax.set_title(
        f"Temperature starting from {df['Timestamp'].iloc[0].strftime('%Y-%m-%d-%H-%M')}"
    )
    date_form = DateFormatter("%H:00")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), ha="right")
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()

    temp_plot = BytesIO()
    plt.savefig(temp_plot, format="png")
    temp_plot.seek(0)
    plt.close()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["Timestamp"], df["Humidity (%)"], color="#4d9f94", linestyle="-")
    ax.set(xlabel="Time", ylabel="Humidity (%)")
    ax.set_ylim(30, 100)
    ax.set_title("Humidity")
    date_form = DateFormatter("%H:00")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), ha="right")
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()

    humidity_plot = BytesIO()
    plt.savefig(humidity_plot, format="png")
    humidity_plot.seek(0)
    plt.close()
    return temp_plot, humidity_plot

def get_photos(num_photos):
    directory = "/home/justin/plantmon/plantmon/pics/"
    photo_files = [
        os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".jpg")
    ]
    latest_photos = sorted(photo_files, key=os.path.getmtime, reverse=True)[:num_photos]
    return [{"filepath": photo, "filename": os.path.basename(photo), "date": datetime.fromtimestamp(os.path.getmtime(photo)).strftime('%Y-%m-%d %H:%M:%S')} for photo in latest_photos]

@app.route("/")
def index():
    df = generate_dummy_data(24)
    temp_plot, humidity_plot = plot(df)

    temperature_plot_data = base64.b64encode(temp_plot.getvalue()).decode("utf8")
    humidity_plot_data = base64.b64encode(humidity_plot.getvalue()).decode("utf8")

    recent_photos = get_photos(3)

    return render_template(
        "index.html",
        temperature_plot=temperature_plot_data,
        humidity_plot=humidity_plot_data,
        recent_photos=recent_photos
    )

@app.route("/plant_photo/<path:filename>")
def serve_photo(filename):
    directory = "/home/justin/plantmon/plantmon/pics/"
    return send_file(os.path.join(directory, filename), mimetype='image/jpeg')


if __name__ == "__main__":
    app.run(debug=True)
