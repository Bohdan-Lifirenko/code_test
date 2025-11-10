import logging

def setup_logging(log_level: str = 'INFO', log_file: str = "app.log") -> None:
    """Setup global logging."""
    level = logging.getLevelName(log_level)
    logger = logging.getLogger()
    logger.setLevel(level)

    console = logging.StreamHandler()
    file = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s %(threadName)s:[%(levelname)s] %(name)s: %(message)s")
    console.setFormatter(formatter)
    file.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(file)

    from pymodbus import pymodbus_apply_logging_config
    pymodbus_apply_logging_config("INFO" if level == logging.DEBUG else "WARNING")