# -*- coding: utf-8 -*-


def get_object(s3_client, s3uri: str) -> str:
    """
    从 S3 中读取一个对象, 并返回其文本内容.
    """
    parts = s3uri.split("/", 3)
    bucket, key = parts[2], parts[3]
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read().decode("utf-8")


def put_object(s3_client, s3uri: str, body: str):
    """
    将一个 JSON 对象保存到 S3 中.
    """
    parts = s3uri.split("/", 3)
    bucket, key = parts[2], parts[3]
    return s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType="application/json",
    )
