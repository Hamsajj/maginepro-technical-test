import logging
import os

import boto3
from botocore import exceptions
import moviepy.editor as mp


def resize_video(video_path: str, output_path: str, height: int = 360, verbose=True):
    clip = mp.VideoFileClip(video_path)
    logging.info(f"starting resizing '{video_path}'")
    clip_resized = clip.resize(height=height)
    create_file_dir(output_path)
    clip_resized.write_videofile(output_path, verbose=verbose, logger="bar" if verbose else None)
    logging.info(f"video resized and saved at '{output_path}'")


def upload_to_s3(file_to_upload: str, bucket_name: str, object_key: str):
    logging.info(f"uploading {file_to_upload} to bucket '{bucket_name}'")
    s3_client = boto3.client("s3")
    s3_client.upload_file(file_to_upload, bucket_name, object_key)
    logging.info(f"upload completed - 's3://{bucket_name}/{object_key}'")


def create_file_dir(file_path: str):
    dirname = os.path.dirname(os.path.abspath(file_path))
    if not os.path.exists(dirname):
        os.makedirs(dirname)
