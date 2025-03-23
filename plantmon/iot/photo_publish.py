"""
uploads captured photos to S3 bucket
"""

import boto3
from botocore.exceptions import ClientError
import logging
import os
from plantmon.config import config

PIC_PATH = config["PIC_PATH"]
BUCKET_NAME = config["AWS_PICS_BUCKET"]


def upload_file(file_name, bucket, object_name):
    """Upload a file to an S3 bucket"""
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} was uploaded to {bucket}/{object_name}")
    except ClientError as e:
        print("File upload failed")
        logging.error(e)
        raise e


if __name__ == "__main__":
    files = os.listdir(PIC_PATH)
    full_paths = [os.path.join(PIC_PATH, file) for file in files]
    latest_pic = max(full_paths, key=os.path.getmtime)
    object_name = os.path.splitext(os.path.basename(latest_pic))[0]
    upload_file(latest_pic, BUCKET_NAME, object_name)
