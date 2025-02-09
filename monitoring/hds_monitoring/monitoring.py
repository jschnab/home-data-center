import time
from datetime import datetime
from statistics import mean

import psutil as psu

from hds_monitoring import (
    config,
    io,
    models,
    systemd,
)

REPETITIONS = 5
COLLECT_INTERVAL_SEC = 1
SLEEP_SEC = 60

DISK_PATH = "/"


def get_load_avg_1_min():
    load = psu.getloadavg()
    load_pct = [ld / psu.cpu_count() * 100 for ld in load]
    return load_pct[0]


def collect_metrics(interval=COLLECT_INTERVAL_SEC, rep=REPETITIONS):
    cpu_pct = []
    cpu_load_pct = []
    mem_avail = []
    mem_pct = []
    mem_swap_used = []
    mem_swap_pct = []
    disk_used = []
    disk_used_pct = []
    disk_read_cnt = []
    disk_write_cnt = []
    disk_read_bytes = []
    disk_write_bytes = []
    net_bytes_sent = []
    net_bytes_recv = []
    net_err_in = []
    net_err_out = []

    cpu_cnt = psu.cpu_count()
    mem_total = psu.virtual_memory().total
    swap_total = psu.swap_memory().total
    disk_total = psu.disk_usage(DISK_PATH).total

    for _ in range(rep):
        cpu_pct.append(psu.cpu_percent())
        cpu_load_pct.append(get_load_avg_1_min())

        mem = psu.virtual_memory()
        mem_avail.append(mem.available)
        mem_pct.append(mem.percent)

        swap = psu.swap_memory()
        mem_swap_used.append(swap.used)
        mem_swap_pct.append(swap.percent)

        disk = psu.disk_usage(DISK_PATH)
        disk_used.append(disk.used)
        disk_used_pct.append(disk.percent)

        disk_io = psu.disk_io_counters()
        disk_read_cnt.append(disk_io.read_count)
        disk_write_cnt.append(disk_io.write_count)
        disk_read_bytes.append(disk_io.read_bytes)
        disk_write_bytes.append(disk_io.write_bytes)

        net = psu.net_io_counters()
        net_bytes_sent.append(net.bytes_sent)
        net_bytes_recv.append(net.bytes_recv)
        net_err_in.append(net.errin)
        net_err_out.append(net.errout)

        time.sleep(interval)

    return models.Metrics(
        config.config["server_name"],
        datetime.now(),
        cpu_cnt,
        mean(cpu_pct),
        mean(cpu_load_pct),
        mem_total,
        mean(mem_avail),
        mean(mem_pct),
        swap_total,
        mean(mem_swap_used),
        mean(mem_swap_pct),
        disk_total,
        mean(disk_used),
        mean(disk_used_pct),
        mean(disk_read_cnt),
        mean(disk_write_cnt),
        mean(disk_read_bytes),
        mean(disk_write_bytes),
        mean(net_bytes_sent),
        mean(net_bytes_recv),
        mean(net_err_in),
        mean(net_err_out),
    )


def monitor(interval=SLEEP_SEC):
    while True:
        metrics = collect_metrics()
        io.metrics_to_csv(metrics)
        active_units = systemd.all_active_units(config.config["systemd_units"])
        for unit in active_units:
            io.services_to_csv(unit)
        time.sleep(interval)
