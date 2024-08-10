from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from io import BytesIO
import base64
import pandas as pd
import os
from datetime import datetime

DATA_DIR = "../sensor_data"
app = Flask(__name__)


def plot(df):
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["Timestamp"], df["Temperature (°C)"], color="#b25c5c", linestyle="-")
    ax.set(xlabel="Time", ylabel="Temperature (°C)")
    ax.set_ylim(15, 35)
    ax.set_title(
        f"Temperature starting from {df['Timestamp'].iloc[0].strftime('%Y-%m-%d-%H-%m')})"  # noqa: E501
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


@app.route("/")
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    data_path = os.path.join(DATA_DIR, f"{today}.csv")
    df = pd.read_csv(data_path)
    temp_plot, humidity_plot = plot(df)

    temperature_plot_data = base64.b64encode(temp_plot.getvalue()).decode("utf8")
    humidity_plot_data = base64.b64encode(humidity_plot.getvalue()).decode("utf8")
    return render_template(
        "index.html",
        temperature_plot=temperature_plot_data,
        humidity_plot=humidity_plot_data,
    )


@app.route("/plant_photo")
def plant_photo():
    directory = "/home/justin/plantmon/plantmon/pics/"
    photo_files = [
        os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.jpg')
        ]
    latest_photo = max(photo_files, key=os.path.getmtime)
    return send_file(latest_photo, mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(debug=True)
