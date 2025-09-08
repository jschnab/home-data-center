import os
from datetime import datetime, timedelta

import boto3

from hds_monitoring import log

S3 = boto3.client("s3")
LOGGER = log.get_logger(__name__)


def modified_last_two_days(path: str) -> bool:
    """
    Return True if the file indicated by the provided path was modified in the
    past 2 days, otherwise return False.
    """
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    return mtime >= datetime.now() - timedelta(days=2)


def copy_folder_to_s3(folder, bucket, key_prefix):
    """
    Copies files stored in the path 'folder' to an S3 bucket.

    The path 'folder' must be an absolute path.

    If there are any sub-folders, they are ignored.
    """
    key_prefix = key_prefix.rstrip("/")
    for file_path in os.listdir(folder):
        full_path = os.path.join(folder, file_path)
        if os.path.isfile(full_path) and modified_last_two_days(full_path):
            key = f"{key_prefix}/{file_path}"
            LOGGER.debug(f"Uploading '{full_path}' to 's3://{bucket}/{key}")
            S3.upload_file(full_path, bucket, key)
