# backend/app/services/files.py
import boto3
from botocore.client import Config
from app.config import settings
from urllib.parse import urljoin
import os

def s3_client():
    endpoint = settings.S3_ENDPOINT
    cfg = {}
    if endpoint:
        cfg["endpoint_url"] = endpoint
    client = boto3.client(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
        config=Config(signature_version="s3v4"),
        **cfg
    )
    return client

def put_object(key: str, data: bytes, content_type: str):
    cl = s3_client()
    cl.put_object(Bucket=settings.S3_BUCKET, Key=key, Body=data, ContentType=content_type)

def presign_put_url(key: str, expires: int = 3600):
    cl = s3_client()
    url = cl.generate_presigned_url('put_object',
                                    Params={'Bucket': settings.S3_BUCKET, 'Key': key},
                                    ExpiresIn=expires)
    return url

def presign_get_url(key: str, expires: int = 3600):
    cl = s3_client()
    url = cl.generate_presigned_url('get_object', Params={'Bucket': settings.S3_BUCKET, 'Key': key}, ExpiresIn=expires)
    return url

