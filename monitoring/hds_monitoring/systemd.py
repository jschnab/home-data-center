import subprocess
from datetime import datetime

from hds_monitoring.config import config
from hds_monitoring.models import SystemdUnit


def is_unit_active(name):
    stat = subprocess.call(["systemctl", "is-active", "--quiet", name])
    return stat == 0


def all_active_units(names):
    return tuple(
        SystemdUnit(
            config["server_name"],
            datetime.now(),
            unit_name,
            is_unit_active(unit_name),
        )
        for unit_name in names
    )
