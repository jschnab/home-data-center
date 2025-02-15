# Description

Collects server metrics (CPU, memory, disk, network) and Systemd service
statuses, then stores them in AWS S3.

# How to use

Clone this repository in the server that you want to monitor, then fill in
variables at the top of the `install` script, and finally run it with superuser
privileges.
