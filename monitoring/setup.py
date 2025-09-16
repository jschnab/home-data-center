from setuptools import find_packages, setup

AUTHOR = "Jonathan Schnabel"
LICENSE = "GNU General Public Licence v3.0"
NAME = "hds-monitoring"
VERSION = "0.4.0"

setup(
    name=NAME,
    packages=find_packages(include=["hds_monitoring", "hds_monitoring.*"]),
    entry_points={
        "console_scripts": ["hds-monitoring=hds_monitoring.main:main"],
    },
    version=VERSION,
    author=AUTHOR,
    license=LICENSE,
    install_requires=["boto3", "psutil"],
)
