from flask import Flask, render_template, send_file
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from io import BytesIO
import base64
import pandas as pd
from datetime import datetime, timedelta
import boto3

app = Flask(__name__)

# Configure AWS details
S3_BUCKET_NAME = "plant-pics"
AWS_REGION = "eu-central-1"
s3_client = boto3.client("s3", region_name=AWS_REGION)



projects = [
    {
        "id": "project1",
        "name": "Project 1",
        "description": "A brief description of Project 1 and its key features.",
        "image": "/static/images/placeholder.svg",
        "link": "#"
    },
    {
        "id": "project2",
        "name": "Project 2",
        "description": "An overview of Project 2 and what makes it unique.",
        "image": "/static/images/placeholder.svg",
        "link": "#"
    },
    {
        "id": "project3",
        "name": "Project 3",
        "description": "Highlighting the main aspects and achievements of Project 3.",
        "image": "/static/images/placeholder.svg",
        "link": "#"
    },
    {
        "id": "project4",
        "name": "Project 4",
        "description": "Exploring the innovative solutions implemented in Project 4.",
        "image": "/static/images/placeholder.svg",
        "link": "#"
    }
]


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


def get_photos(num_photos):
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, MaxKeys=num_photos)

        photos = []
        for obj in response.get("Contents", []):
            photo = {
                "key": obj["Key"],
                "filename": obj["Key"].split("/")[-1],
                "date": obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
                "url": s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_BUCKET_NAME, "Key": obj["Key"]},
                    ExpiresIn=3600,
                ),
            }
            photos.append(photo)

        # Sort the photos by date, most recent first
        photos.sort(key=lambda x: x["date"], reverse=True)

        return photos[:num_photos]
    except Exception as e:
        print(f"Error retrieving photos from S3: {e}")
        return []

@app.route('/')
def home():
    return render_template('home.html', projects=projects[2:])

@app.route('/plantmonitor-dynamic')
def plant_monitor():
    df = get_sensor_data()
    temp_plot, humidity_plot = plot(df)

    temperature_plot_data = base64.b64encode(temp_plot.getvalue()).decode("utf8")
    humidity_plot_data = base64.b64encode(humidity_plot.getvalue()).decode("utf8")

    recent_photos = get_photos(3)

    return render_template(
        'plantmon/dashboard.html',
        temperature_plot=temperature_plot_data,
        humidity_plot=humidity_plot_data,
        recent_photos=recent_photos,
    )

if __name__ == "__main__":
    app.run(debug=True)
