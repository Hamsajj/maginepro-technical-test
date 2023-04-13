import json
import logging
import os
import subprocess

import boto3
from botocore.exceptions import ClientError



def thumbnail_creator(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    saved_objects = []
    dest_s3_bucket = os.getenv("THUMBNAIL_S3") or 'maginepro-thumbnail'
    for record in event["Records"]:
        event_s3_data = record['s3']
        downloaded_video = download_s3_object(bucket_name=event_s3_data['bucket']["name"],
                                  object_name=event_s3_data['object']["key"])
        thumbnail_name = os.path.splitext(event_s3_data['object']["key"])[0] + "_thumbnail.jpeg"
        image_file = extract_thumbnail(downloaded_video, thumbnail_name)
        saved_object = upload_to_s3(image_file, dest_s3_bucket, thumbnail_name)
        saved_objects.append(saved_object)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "thumbnails": saved_objects,
        }),
    }


def extract_thumbnail(video_path: str, output_name: str):
    output_file = f"/tmp/{output_name}"
    ffmpeg_exe = os.getenv("FFMPEG_BIN")
    command = f"{ffmpeg_exe} -i '{video_path}' -ss 00:00:01.000 -vframes 1 {output_file}"
    p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output, err = p.communicate()
    if err is not None:
        logging.error(f"error using ffmpeg to extract thumbnail: {err}")
        raise Exception(err)
    return output_file


def upload_to_s3(file_to_upload: str, bucket_name: str, object_key: str):
    logging.info(f"uploading {file_to_upload} to bucket '{bucket_name}'")
    s3_client = boto3.client("s3")
    s3_client.upload_file(file_to_upload, bucket_name, object_key)
    logging.info(f"upload completed - 's3://{bucket_name}/{object_key}'")
    return f's3://{bucket_name}/{object_key}'


def download_s3_object(bucket_name, object_name, expiration=60):
    s3 = boto3.client('s3')
    filename = f"/tmp/{object_name}"

    try:
        with open(filename, 'wb') as f:
            s3.download_fileobj(bucket_name, object_name, f)
        return filename
    except ClientError as e:
        logging.error(e)
        return None
