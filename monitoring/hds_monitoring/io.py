import csv
import os
from datetime import date, datetime, timedelta, timezone

from hds_monitoring import models, settings
from hds_monitoring.config import config


def to_csv(row, field_names, file_path):
    with open(file_path, "a") as fi:
        writer = csv.DictWriter(fi, fieldnames=field_names)
        writer.writerow(row._asdict())


def metrics_to_csv(row):
    date_str = date.today().strftime(settings.DATE_FORMAT)
    file_path = os.path.join(
        config["data_dir"], f"metrics_{date_str}{settings.FILE_EXT}"
    )
    to_csv(row, models.METRICS_FIELD_NAMES, file_path)


def services_to_csv(row):
    date_str = date.today().strftime(settings.DATE_FORMAT)
    file_path = os.path.join(
        config["data_dir"], f"services_{date_str}{settings.FILE_EXT}"
    )
    to_csv(row, models.SYSTEMD_UNITS_FIELD_NAMES, file_path)


def cleanup_logs():
    for path in os.listdir(config["data_dir"]):
        full_path = os.path.join(settings.DATA_DIR, path)
        last_modified_at = datetime.utcfromtimestamp(full_path)
        now = datetime.now(tz=timezone.utc)
        if now - last_modified_at < timedelta(days=7):
            os.remove(full_path)
