import os
import re
from io import BytesIO

import boto3

from models import S3File


class S3Client:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        self.bucket_path = os.getenv("AWS_BUCKET_PATH")

    def list_files(self):
        response = self.s3.list_objects_v2(
            Bucket=self.bucket_name, Prefix=self.bucket_path
        )
        contents = response.get("Contents", [])

        s3_files = []
        for obj in contents:
            if obj["Key"] != self.bucket_path:
                try:
                    file_response = self.s3.get_object(
                        Bucket=self.bucket_name, Key=obj["Key"]
                    )
                    file_content = file_response["Body"].read().decode("utf-8")
                except Exception as e:
                    print(f"Error reading content for {obj['Key']}: {e}")
                    file_content = None

                s3_files.append(
                    S3File(
                        bucket=self.bucket_name,
                        key=obj["Key"],
                        uuid=self._extract_uuid(obj["Key"]),
                        last_modified=obj["LastModified"],
                        url=self._get_presigned_url(obj["Key"]),
                        content=file_content,
                    )
                )

        return s3_files

    def upload_file(self, file: bytes, uuid: str, name: str):
        file_obj = BytesIO(file)
        file_name = f"{uuid}/{name}"
        file_path = f"{self.bucket_path}{file_name}"

        self.s3.upload_fileobj(file_obj, self.bucket_name, file_path)

    def _extract_uuid(self, key: str):
        uuid_match = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            key,
        )
        return uuid_match.group(0) if uuid_match else ""

    def _get_presigned_url(self, key: str):
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=300,
        )
