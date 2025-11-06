import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#pymodbus_apply_logging_config("INFO")

# Create handlers
console = logging.StreamHandler()
file = logging.FileHandler("app.log")

# Create formatter
formatter = logging.Formatter("%(asctime)s %(threadName)s:[%(levelname)s] %(name)s: %(message)s")

# Attach formatter to handlers
console.setFormatter(formatter)
file.setFormatter(formatter)

# Attach handlers to logger
logger.addHandler(console)
logger.addHandler(file)
from db_communication import archive_to_sqlite

class FakeTCPClient:
    def __init__(
            self,
            slaves_config):
        self.slaves_config = slaves_config

    def start_polling(self):
        current_configs = self.slaves_config
        while True:
            for conf in current_configs:
                archive_to_sqlite(self.data_dir, conf['slave_id'], "8,86")
                logger.info(
                    f"Polling slave {conf['slave_id']}, register {conf['address']} value 8,86")
            time.sleep(1)  # Poll every second