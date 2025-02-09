from configparser import ConfigParser

from hds_monitoring import settings


def parse_config(config):
    default = config["default"]
    units = tuple(default["systemd_units"].split(","))
    return {
        "server_name": default["server_name"],
        "systemd_units": units,
        "data_dir": default["data_dir"],
    }


def get_config(config_file=settings.CONFIG_FILE):
    config = ConfigParser(interpolation=None)
    config.read(config_file)
    return parse_config(config)


config = get_config()
