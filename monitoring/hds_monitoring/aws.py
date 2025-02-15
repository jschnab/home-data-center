import os

import boto3

from hds_monitoring import log

S3 = boto3.client("s3")
LOGGER = log.get_logger(__name__)


def copy_folder_to_s3(folder, bucket, key_prefix):
    """
    Copies files stored in the path 'folder' to an S3 bucket.

    The path 'folder' must be an absolute path.

    If there are any sub-folders, they are ignored.
    """
    key_prefix = key_prefix.rstrip("/")
    for file_path in os.listdir(folder):
        full_path = os.path.join(folder, file_path)
        if os.path.isfile(full_path):
            key = f"{key_prefix}/{file_path}"
            LOGGER.debug(f"Uploading '{full_path}' to 's3://{bucket}/{key}")
            S3.upload_file(full_path, bucket, key)
