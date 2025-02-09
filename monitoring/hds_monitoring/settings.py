import os

APP_DIR = os.getenv("HDS_MONITORING_APP_DIR")
CONFIG_FILE = os.path.join(APP_DIR, os.getenv("HDS_MONITORING_CONFIG_FILE"))
DATE_FORMAT = "%Y-%m-%d"
FILE_EXT = ".csv"
