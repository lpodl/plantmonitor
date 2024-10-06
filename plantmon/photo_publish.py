"""
captures photos and uploads them to S3 bucket
"""

import boto3
from datetime import datetime

s3 = boto3.client("s3")
bucket_name = "plant-monitoring-images-yourusername"


def upload_image_to_s3(image_data, image_name):
    try:
        s3.put_object(Bucket=bucket_name, Key=image_name, Body=image_data)
        print(f"Uploaded {image_name} to S3 successfully")
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")


# In your image capture function:
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
image_name = f"plant_image_{timestamp}.jpg"
# Capture image (replace with your actual image capture code)
image_data = capture_image()
upload_image_to_s3(image_data, image_name)
