import boto3
from botocore.exceptions import ClientError

# Replace with your actual S3 bucket name
S3_BUCKET_NAME = "plant-pics"
AWS_REGION = "eu-central-1"  # Replace with your AWS region if different


def test_s3_connection():
    try:
        # Create an S3 client
        s3_client = boto3.client("s3", region_name=AWS_REGION)

        # Try to list objects in the bucket
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, MaxKeys=1)

        if "Contents" in response:
            print(f"Successfully connected to S3 bucket: {S3_BUCKET_NAME}")
            print(f"First object key: {response['Contents'][0]['Key']}")
        else:
            print(
                f"Successfully connected to S3 bucket: {S3_BUCKET_NAME}, but it's empty"
            )

        return True

    except ClientError as e:
        print(f"Failed to connect to S3 bucket: {e}")
        return False


def get_photos2(num_photos):
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
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
        print([x["filename"] for x in photos])
        photos.sort(key=lambda x: x["date"], reverse=True)
        print("sorted:")

        return photos[:num_photos]
    except Exception as e:
        print(f"Error retrieving photos from S3: {e}")
        return []


from datetime import datetime, timedelta


def get_date_prefixes():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    today_prefix = today.strftime("%Y-%m-%d")
    yesterday_prefix = yesterday.strftime("%Y-%m-%d")
    return today_prefix, yesterday_prefix


def get_photos(num_photos):
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    today_prefix, yesterday_prefix = get_date_prefixes()

    photos = []
    for prefix in [today_prefix, yesterday_prefix]:
        try:
            response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
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

            if len(photos) >= num_photos:
                break
        except Exception as e:
            print(f"Error retrieving photos from S3 for prefix {prefix}: {e}")

    # Sort the photos by date, most recent first
    photos.sort(key=lambda x: x["date"], reverse=True)
    print([x["filename"] for x in photos[:num_photos]])
    return photos[:num_photos]


if __name__ == "__main__":
    test_s3_connection()
    get_photos(3)
