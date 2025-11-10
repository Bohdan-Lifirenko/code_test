import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logging(log_level: str = 'INFO', log_file_path: str = "app.log") -> None:
    """Setup global logging."""
    level = logging.getLevelName(log_level)
    logger = logging.getLogger()
    logger.setLevel(level)

    console = logging.StreamHandler()
    #file = logging.FileHandler(log_file_path)

    # Ротація по днях: новий файл щодня о півночі
    file_handler = TimedRotatingFileHandler(
        log_file_path,  # Базова назва файлу (поточний день)
        when='midnight',  # Ротація о півночі
        interval=1,  # Кожні 1 "одиницю" (тут — день)
        backupCount=30  # Зберігати до 30 старих файлів (опціонально)
    )

    formatter = logging.Formatter("%(asctime)s %(threadName)s:[%(levelname)s] %(name)s: %(message)s")
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(file_handler)

    from pymodbus import pymodbus_apply_logging_config
    pymodbus_apply_logging_config("INFO" if level == logging.DEBUG else "WARNING")