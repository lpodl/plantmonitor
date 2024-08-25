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


if __name__ == "__main__":
    test_s3_connection()
