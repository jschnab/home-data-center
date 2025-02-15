from hds_monitoring import monitoring, log

LOGGER = log.get_logger(__name__)


def main():
    LOGGER.info("Starting application")
    monitoring.monitor()


if __name__ == "__main__":
    main()
