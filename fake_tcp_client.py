import threading
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
            polling_period,
            slaves_config,
            data_dir
    ):
        self.polling_period = polling_period
        self.slaves_config = slaves_config
        self.data_dir = data_dir

    def start_polling(self):
        def poll_modbus_rtu():
            current_configs = self.slaves_config
            while True:
                for conf in current_configs:
                    archive_to_sqlite(self.data_dir, conf['slave_id'], "8,86")
                    logger.info(
                        f"Polling slave {conf['slave_id']}, register {conf['address']} value 8,86")
                time.sleep(1)  # Poll every second

        polling_thread = threading.Thread(target=poll_modbus_rtu, daemon=True)
        polling_thread.start()

        logger.info(f"ModbusRTUDataCollector started polling with polling period = {self.polling_period} sec.")