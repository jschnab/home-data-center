import csv
import os
from datetime import date, datetime, timedelta

from hds_monitoring import models, settings
from hds_monitoring.config import config


def to_csv(row, field_names, file_path):
    if os.path.exists(file_path):
        new_file = False
    else:
        new_file = True
    with open(file_path, "a") as fi:
        writer = csv.DictWriter(fi, fieldnames=field_names)
        if new_file:
            writer.writeheader()
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
        full_path = os.path.join(config["data_dir"], path)
        last_modified_at = datetime.utcfromtimestamp(
            os.path.getmtime(full_path)
        )
        now = datetime.now()
        if now - last_modified_at < timedelta(days=7):
            os.remove(full_path)
