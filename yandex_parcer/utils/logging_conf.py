def get_logging_conf():
    logging_conf = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "stream_format": {
                "format": "%(asctime)s\t%(levelname)s:\t%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "stream_handler": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "stream_format",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["stream_handler"],
        },
    }
    return logging_conf
