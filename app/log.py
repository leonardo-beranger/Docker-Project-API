import os
import logging.config


def setup_logging(file_path):

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(levelname)s: %(message)s"},
            "detailed": {
                "format": "[%(levelname)s|%(module)s|LINE-%(lineno)d] %(asctime)s: %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
        },
        "handlers": {
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stderr",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": file_path,
                "maxBytes": 10000,
                "backupCount": 3,
            },
        },
    }

    logging_config["loggers"] = {"root": {"level": "DEBUG", "handlers": ["stderr", "file"]}}

    if os.environ.get("PRODUCTION"):
        logging_config["loggers"] = {"root": {"level": "INFO", "handlers": ["stderr", "file"]}}
    

    logging.config.dictConfig(config=logging_config)
