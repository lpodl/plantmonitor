from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from io import BytesIO
import base64
import pandas as pd
from datetime import datetime, timedelta, timezone
import boto3
from zoneinfo import ZoneInfo


app = Flask(__name__)

# Configure AWS details
S3_BUCKET_NAME = "plant-pics"
AWS_REGION = "eu-central-1"
s3_client = boto3.client("s3", region_name=AWS_REGION)


projects = [
    {
        "id": "plantmon-dynamic",
        "name": "Plantmonitor - Dynamic",
        "description": "Website for monitoring plant health using AWS, Flask and nginx.",
        "image": "/static/img/plantmon-dynamic.png",
        "github_url": "https://github.com/yourusername/plantmon-dynamic",
        "live_url": "/plantmonitor-dynamic",
        "details_url": "/projects/plantmon-dynamic",
        "category": "plantmon",
    },
    {
        "id": "plantmon-static",
        "name": "Plantmonitor - Static",
        "description": "Static version of the plant monitoring system.",
        "image": "/static/img/placeholder.jpg",
        "github_url": "https://github.com/yourusername/plantmon-static",
        "live_url": "https://static.plantmonitor.yourdomain.com",  # github.io
        "details_url": "/projects/plantmon-static",
        "category": "plantmon",
    },
    {
        "id": "autoqubo",
        "name": "AutoQUBO",
        "description": "Translating problems for quantum computers using Python.",
        "image": "/static/img/chimera-topology.png",
        "github_url": "https://github.com/yourusername/autoqubo",
        "details_url": "/projects/autoqubo",
        "category": "quantum",
    },
    {
        "id": "webcrawler",
        "name": "Webcrawler",
        "description": "A webcrawler to check for dead links written in JavaScript.",
        "image": "/static/img/webcrawler.png",
        "github_url": "https://github.com/yourusername/webcrawler",
        "details_url": "/projects/webcrawler",
        "category": "js",
    },
]


# /home
@app.route("/")
def home():
    return render_template("home.html", projects=projects)


@app.route("/cv")
def download_cv():
    try:
        return send_file("static/cv_pauckert.pdf", as_attachment=True)
    except FileNotFoundError:
        return "CV file not found", 404


# /projects
@app.route("/projects/<project_id>")
def project_details(project_id):
    project = next((p for p in projects if p["id"] == project_id), None)
    if project is None:
        return "Project not found", 404
    return render_template("projects/details.html", project=project)


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


def get_photos(num_photos):
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

    # Sort the photos by date, most recent first
    photos.sort(key=lambda x: x["date"], reverse=True)
    return photos[:num_photos]


@app.route("/plantmonitor-dynamic")
def plant_monitor():
    df = get_sensor_data()
    temp_plot, humidity_plot = plot(df)

    temperature_plot_data = base64.b64encode(temp_plot.getvalue()).decode("utf8")
    humidity_plot_data = base64.b64encode(humidity_plot.getvalue()).decode("utf8")

    recent_photos = get_photos(3)

    return render_template(
        "plantmon/dashboard.html",
        temperature_plot=temperature_plot_data,
        humidity_plot=humidity_plot_data,
        recent_photos=recent_photos,
    )


if __name__ == "__main__":
    app.run(debug=True)
