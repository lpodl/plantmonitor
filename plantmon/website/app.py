import base64
import os
import re
from datetime import datetime, timedelta, timezone
from io import BytesIO
from zoneinfo import ZoneInfo
import logging

import boto3
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, send_file, url_for
from matplotlib.dates import DateFormatter

from plantmon.config import config

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Configure AWS details
S3_BUCKET_NAME = config["AWS_PICS_BUCKET"]
AWS_REGION = config["AWS_REGION"]
s3_client = boto3.client("s3", region_name=AWS_REGION)


# /home
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/cv.pdf")
def download_cv():
    try:
        return send_file("static/cv_pauckert.pdf", as_attachment=True)
    except FileNotFoundError:
        return "CV file not found", 404


# /plantmon
def get_sensor_data():
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    table = dynamodb.Table("SensorData")
    week_ago = datetime.today() - timedelta(weeks=1)
    week_ago = week_ago.strftime("%Y-%m-%d %H:%M:%S")
    response = table.query(
        KeyConditionExpression="msg_id = :msg_id AND msg_time > :timestamp",
        ExpressionAttributeValues={":msg_id": "0", ":timestamp": week_ago},
    )
    return pd.DataFrame(response["Items"])


def plot(df):
    df["msg_time"] = pd.to_datetime(df["msg_time"])
    df = df.sort_values("msg_time")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["msg_time"], df["temperature"], color="#b25c5c", linestyle="-")
    ax.set(xlabel="Time", ylabel="Temperature (°C)")
    ax.set_ylim(15, 35)
    date_form = DateFormatter("%H:00\n%m/%d")
    temp_plot = BytesIO()
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(temp_plot, format="png", bbox_inches="tight")
    temp_plot.seek(0)
    plt.close()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["msg_time"], df["humidity"], color="#4d9f94", linestyle="-")
    ax.set(xlabel="Time", ylabel="Humidity (%)")
    ax.set_ylim(30, 100)
    date_form = DateFormatter("%H:00\n%m/%d")
    ax.xaxis.set_major_formatter(date_form)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
    plt.setp(ax.xaxis.get_majorticklabels(), ha="right")
    ax.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    humidity_plot = BytesIO()
    plt.savefig(humidity_plot, format="png", bbox_inches="tight")
    humidity_plot.seek(0)
    plt.close()
    return temp_plot, humidity_plot


def get_date_prefixes():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    today_prefix = today.strftime("%Y-%m-%d")
    yesterday_prefix = yesterday.strftime("%Y-%m-%d")
    return today_prefix, yesterday_prefix


def convert_utc_to_berlin(utc_dt):
    """needed bc LastModified in DynamoDB is UTC"""
    berlin_zone = ZoneInfo("Europe/Berlin")
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(berlin_zone)


def get_default_images(pattern=r"default_img_\d+\.png"):
    """
    Scans the static/img directory for default images matching the pattern.
    Returns a list of filenames sorted by their number.
    """
    img_dir = os.path.join(app.static_folder, "img")
    default_images = []

    for filename in os.listdir(img_dir):
        if re.match(pattern, filename):
            default_images.append(filename)

    # Sort by the number in the filename
    default_images.sort(key=lambda x: int(re.search(r"(\d+)", x).group()))
    return default_images


def get_photos(num_photos=3):
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    # only query recent pics, then sort by time
    today_prefix, yesterday_prefix = get_date_prefixes()
    photos = []
    for prefix in [today_prefix, yesterday_prefix]:
        try:
            response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
            for obj in response.get("Contents", []):
                berlin_time = convert_utc_to_berlin(obj["LastModified"])
                photo = {
                    "key": obj["Key"],
                    "filename": obj["Key"].split("/")[-1],
                    "date": berlin_time.strftime("%Y-%m-%d %H:%M"),
                    "url": s3_client.generate_presigned_url(
                        "get_object",
                        Params={"Bucket": S3_BUCKET_NAME, "Key": obj["Key"]},
                        ExpiresIn=3600,
                    ),
                }
                photos.append(photo)

            if len(photos) >= num_photos:
                break
        except Exception as e:
            print(f"Error retrieving photos from S3 for prefix {prefix}: {e}")

    # default photos if there aren't enough recent ones
    if len(photos) < num_photos:
        default_filenames = get_default_images()
        if default_filenames:
            # Use available default images (up to num_photos)
            for i, filename in enumerate(default_filenames[: num_photos - len(photos)]):
                photos.append(
                    {
                        "key": f"default-{i+1}",
                        "filename": filename,
                        "date": f"default image {i+1}",
                        "url": url_for("static", filename=f"img/{filename}"),
                    }
                )
        else:
            print("No default images found in static/img directory")

    # Sort the photos by date, most recent first
    photos.sort(key=lambda x: x["date"], reverse=True)
    return photos[:num_photos]


@app.route("/plantmonitor-dynamic")
def plant_monitor():
    df = get_sensor_data()
    temp_plot, humidity_plot = plot(df)

    temperature_plot_data = base64.b64encode(temp_plot.getvalue()).decode("utf8")
    humidity_plot_data = base64.b64encode(humidity_plot.getvalue()).decode("utf8")

    recent_photos = get_photos()

    return render_template(
        "plantmon/dashboard.html",
        temperature_plot=temperature_plot_data,
        humidity_plot=humidity_plot_data,
        recent_photos=recent_photos,
    )


if __name__ == "__main__":
    app.run(debug=True)
