from collections import namedtuple

METRICS_FIELD_NAMES = [
    "server_name",
    "timestamp",
    "cpu_count",
    "cpu_percent",
    "cpu_load_percent",
    "memory_total",
    "memory_available",
    "memory_used_percent",
    "memory_swap_total",
    "memory_swap_used",
    "memory_swap_used_percent",
    "disk_total",
    "disk_used",
    "disk_used_percent",
    "disk_read_count",
    "disk_write_count",
    "disk_read_bytes",
    "disk_write_bytes",
    "network_bytes_sent",
    "network_bytes_received",
    "network_errors_receiving",
    "network_errors_sending",
]

Metrics = namedtuple("Metrics", METRICS_FIELD_NAMES)

SYSTEMD_UNITS_FIELD_NAMES = [
    "server_name",
    "timestamp",
    "unit_name",
    "active",
]

SystemdUnit = namedtuple("SystemdUnit", SYSTEMD_UNITS_FIELD_NAMES)
