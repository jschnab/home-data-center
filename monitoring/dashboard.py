import csv
import os
import re
from collections import defaultdict, namedtuple
from datetime import datetime, timedelta
from typing import List

import boto3
import dash
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


S3_BUCKET = "home-data-center-monitoring-jschnab"
S3_CLIENT = boto3.client("s3")
S3_DELIM = "/"
DATA_DIR = "dashboard_data"
LOG_DATE_REGEX = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}).csv$"
METRICS_LOG_KEY_REGEX = re.compile(r"^.+metrics_" + LOG_DATE_REGEX)
SERVICES_LOG_KEY_REGEX = re.compile(r"^.+services_" + LOG_DATE_REGEX)
TS_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

GIB = 1024 * 1024 * 1024

GRAPH_COLORS = ["blue", "red", "green", "yellow", "purple", "orange"]


def get_server_names_from_s3(
    s3_bucket: str = S3_BUCKET, s3_delimiter: str = S3_DELIM
) -> List[str]:
    response = S3_CLIENT.list_objects_v2(
        Bucket=s3_bucket, Delimiter=s3_delimiter
    )
    return sorted(
        [
            item["Prefix"].rstrip(s3_delimiter)
            for item in response["CommonPrefixes"]
        ]
    )


def get_server_names_from_local(data_dir: str = DATA_DIR) -> List[str]:
    return sorted([path.rstrip("/") for path in os.listdir(data_dir)])


def make_data_dirs(server_names: List[str]) -> None:
    for sn in server_names:
        os.makedirs(os.path.join(DATA_DIR, sn), exist_ok=True)


def get_last_logs(
    server_names: List[str], s3_bucket: str = S3_BUCKET
) -> List[dict]:
    server_logs = {}
    for sname in server_names:
        metrics_keys = []
        services_keys = []
        response = S3_CLIENT.list_objects_v2(Bucket=s3_bucket, Prefix=sname)
        for key in (cont["Key"] for cont in response["Contents"]):
            if (match := METRICS_LOG_KEY_REGEX.match(key)) is not None:
                metrics_keys.append(
                    (
                        key,
                        datetime(
                            int(match["year"]),
                            int(match["month"]),
                            int(match["day"]),
                        ),
                    )
                )
            elif (match := SERVICES_LOG_KEY_REGEX.match(key)) is not None:
                services_keys.append(
                    (
                        key,
                        datetime(
                            int(match["year"]),
                            int(match["month"]),
                            int(match["day"]),
                        ),
                    )
                )
        server_logs[sname] = {
            "metrics": sorted(metrics_keys, key=lambda x: x[1])[-1][0],
            "services": sorted(services_keys, key=lambda x: x[1])[-1][0],
        }
    return server_logs


def download_logs(logs: dict, s3_bucket=S3_BUCKET, data_dir=DATA_DIR) -> None:
    """
    Downloads logs from S3 to local disk.

    The parameter logs is a dictionary formatted as:

    {
        "<server-name-1>: {
            "metrics": "<metrics-logs-s3-key>",
            "services": "<services-logs-s3-key>",
        },
        ...
        "<server-name-n>: {
            "metrics": "<metrics-logs-s3-key>",
            "services": "<services-logs-s3-key>",
        },
    }

    S3 keys are prefixed with the server name, so no need to join with the
    server name when building the local file path.
    """
    for server, logs in logs.items():
        S3_CLIENT.download_file(
            Bucket=s3_bucket,
            Key=logs["metrics"],
            Filename=os.path.join(data_dir, logs["metrics"]),
        )
        S3_CLIENT.download_file(
            Bucket=s3_bucket,
            Key=logs["services"],
            Filename=os.path.join(data_dir, logs["services"]),
        )


def download_last_logs() -> None:
    servers = get_server_names_from_s3()
    make_data_dirs(servers)
    last_logs = get_last_logs(servers)
    download_logs(last_logs)


def app_layout():
    server_names = get_server_names_from_local()

    return [
        html.Title(["Home Data Center Monitoring"]),
        html.Label("Server name:", htmlFor="server-name-drop-down"),
        dcc.Dropdown(
            options=server_names + ["*"],
            value="*",
            id="server-name-drop-down",
        ),
        html.H2("Service Statuses"),
        html.Table(id="service-status-table"),
        html.H2("System parameters"),
        html.Table(id="system-parameters"),
        html.H2("Server Metrics"),
        html.H3("CPU Utilization (%)"),
        dcc.Graph(id="cpu-percent"),
        html.H3("Memory Utilization (%)"),
        dcc.Graph(id="memory-used-percent"),
        html.H3("Disk Utilization (%)"),
        dcc.Graph(id="disk-used-percent"),
    ]


@dash.callback(
    Output(component_id="service-status-table", component_property="children"),
    Input(component_id="server-name-drop-down", component_property="value"),
)
def update_service_status_table(server_name):
    if server_name == "*":
        server_names = get_server_names_from_local()
    else:
        server_names = [server_name]

    log_paths = []
    for sname in server_names:
        dir_name = os.path.join(DATA_DIR, sname)
        log_paths.append(
            sorted(
                [
                    os.path.join(dir_name, path)
                    for path in os.listdir(dir_name)
                    if "services" in path
                ]
            )[-1]
        )

    last_statuses = defaultdict(dict)

    for lpath in log_paths:
        with open(lpath) as fi:
            reader = csv.reader(fi)
            # Read column names from header.
            Data = namedtuple("Data", next(reader))

            for row in map(Data._make, reader):
                if row.unit_name == "":
                    continue
                if row.server_name == server_name or server_name == "*":
                    timestamp = datetime.strptime(row.timestamp, TS_FORMAT)
                    if (
                        last := last_statuses.get(row.server_name, {}).get(
                            row.unit_name
                        )
                    ) is not None:
                        if (
                            timestamp
                            > datetime.strptime(last.timestamp, TS_FORMAT)
                        ):
                            last_statuses[row.server_name][row.unit_name] = row
                    else:
                        last_statuses[row.server_name][row.unit_name] = row

    return html.Table(
        [
            html.Tr(
                [
                    html.Th("Server Name"),
                    html.Th("Service Name"),
                    html.Th("Status"),
                    html.Th("Updated At"),
                ]
            )
        ]
        + [
            html.Tr(
                [
                    html.Td(server_name),
                    html.Td(service_name),
                    html.Td(
                        "active" if row.active.lower() == "true" else "failed"
                    ),
                    html.Td(row.timestamp)
                ]
            )
            for server_name, service in last_statuses.items()
            for service_name, row in service.items()
        ]
    )


@dash.callback(
    Output(component_id="system-parameters", component_property="children"),
    Input(component_id="server-name-drop-down", component_property="value"),
)
def update_system_parameters_table(server_name):
    if server_name == "*":
        server_names = get_server_names_from_local()
    else:
        server_names = [server_name]

    log_paths = []
    for sname in server_names:
        dir_name = os.path.join(DATA_DIR, sname)
        log_paths.extend(
            [
                os.path.join(dir_name, path)
                for path in os.listdir(dir_name)
                if "metrics" in path
            ]
        )

    dfs = []
    for lpath in log_paths:
        dfs.append(pd.read_csv(lpath))
    concat_df = pd.concat(dfs)
    concat_df["timestamp"] = pd.to_datetime(concat_df["timestamp"])

    most_recent = concat_df.groupby("server_name").max("timestamp")

    return html.Table(
        [
            html.Tr(
                [
                    html.Th("Server Name"),
                    html.Th("CPU Count"),
                    html.Th("Total Disk Space (GiB)"),
                    html.Th("Disk Used (GiB)"),
                ]
            )
        ]
        + [
            html.Tr(
                [
                    html.Td(server_name),
                    html.Td(most_recent.loc[server_name].cpu_count),
                    html.Td(
                        f"{most_recent.loc[server_name].disk_total / GIB:.2f}"
                    ),
                    html.Td(
                        f"{most_recent.loc[server_name].disk_used / GIB:.2f}"
                    ),
                ]
            )
            for server_name in most_recent.index
        ]
    )


@dash.callback(
    Output("cpu-percent", "figure"),
    Input("server-name-drop-down", "value"),
)
def update_cpu_percent(server_name):
    if server_name == "*":
        server_names = get_server_names_from_local()
    else:
        server_names = [server_name]

    log_paths = []
    for sname in server_names:
        dir_name = os.path.join(DATA_DIR, sname)
        log_paths.extend(
            [
                os.path.join(dir_name, path)
                for path in os.listdir(dir_name)
                if "metrics" in path
            ]
        )

    dfs = []
    for lpath in log_paths:
        dfs.append(pd.read_csv(lpath))
    concat_df = pd.concat(dfs)
    concat_df["timestamp"] = pd.to_datetime(concat_df["timestamp"])

    ts_cut_df = concat_df[
        concat_df["timestamp"] >= datetime.now() - timedelta(days=1)
    ]

    if server_name == "*":
        final_df = ts_cut_df
    else:
        final_df = ts_cut_df[ts_cut_df["server_name"] == server_name]

    final_df.sort_values(["server_name", "timestamp"], inplace=True)

    return px.line(
        final_df,
        x="timestamp",
        y="cpu_percent",
        line_group="server_name",
        color="server_name",
    )


@dash.callback(
    Output("memory-used-percent", "figure"),
    Input("server-name-drop-down", "value"),
)
def update_memory_used_percent(server_name):
    if server_name == "*":
        server_names = get_server_names_from_local()
    else:
        server_names = [server_name]

    log_paths = []
    for sname in server_names:
        dir_name = os.path.join(DATA_DIR, sname)
        log_paths.extend(
            [
                os.path.join(dir_name, path)
                for path in os.listdir(dir_name)
                if "metrics" in path
            ]
        )

    dfs = []
    for lpath in log_paths:
        dfs.append(pd.read_csv(lpath))
    concat_df = pd.concat(dfs)
    concat_df["timestamp"] = pd.to_datetime(concat_df["timestamp"])

    ts_cut_df = concat_df[
        concat_df["timestamp"] >= datetime.now() - timedelta(days=1)
    ]

    if server_name == "*":
        final_df = ts_cut_df
    else:
        final_df = ts_cut_df[ts_cut_df["server_name"] == server_name]

    final_df.sort_values(["server_name", "timestamp"], inplace=True)

    return px.line(
        final_df,
        x="timestamp",
        y="memory_used_percent",
        line_group="server_name",
        color="server_name",
    )


@dash.callback(
    Output("disk-used-percent", "figure"),
    Input("server-name-drop-down", "value"),
)
def update_disk_used_percent(server_name):
    if server_name == "*":
        server_names = get_server_names_from_local()
    else:
        server_names = [server_name]

    log_paths = []
    for sname in server_names:
        dir_name = os.path.join(DATA_DIR, sname)
        log_paths.extend(
            [
                os.path.join(dir_name, path)
                for path in os.listdir(dir_name)
                if "metrics" in path
            ]
        )

    dfs = []
    for lpath in log_paths:
        dfs.append(pd.read_csv(lpath))
    concat_df = pd.concat(dfs)
    concat_df["timestamp"] = pd.to_datetime(concat_df["timestamp"])

    ts_cut_df = concat_df[
        concat_df["timestamp"] >= datetime.now() - timedelta(days=1)
    ]

    if server_name == "*":
        final_df = ts_cut_df
    else:
        final_df = ts_cut_df[ts_cut_df["server_name"] == server_name]

    final_df.sort_values(["server_name", "timestamp"], inplace=True)

    return px.line(
        final_df,
        x="timestamp",
        y="disk_used_percent",
        line_group="server_name",
        color="server_name",
    )


def run_app(debug):
    app = dash.Dash()
    app.layout = app_layout()
    app.run(debug=debug)


if __name__ == "__main__":
    download_last_logs()
    run_app(debug=True)
