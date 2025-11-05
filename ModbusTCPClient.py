import logging
import os
import sqlite3
import threading
import time
from datetime import date
from datetime import datetime

from pymodbus import pymodbus_apply_logging_config, ModbusException
from pymodbus.client import ModbusSerialClient
from db_communication import load_configs, archive_to_sqlite

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

class ModbusTCPClient:
    def __init__(
            self,
            convertor_port,
            baudrate,
            bytesize,
            parity,
            stopbits,
            polling_period,
            DATA_DIR,
            CONFIG_FILE,
            context
    ):
        self.convertor_port = convertor_port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.polling_period = polling_period

        self.DATA_DIR = DATA_DIR
        self.CONFIG_FILE = CONFIG_FILE

        self.context = context
        self.client = ModbusSerialClient(
            port='COM7',          # Or '/dev/ttyUSB0' on Linux/macOS
            baudrate=9600,        # Match your slave's baud rate
            bytesize=8,
            parity='N',           # 'N' for none, 'E' for even, 'O' for odd
            stopbits=1,
            timeout=2,             # In seconds
            retries=0
        )

        self.is_polling = threading.Event()

    def start_polling(self):
        def poll_modbus_rtu():
            if self.client.connect():
                logger.info("Connected successfully!")
            else:
                logging.error("Failed to connect. Check port, wiring, or parameters.")
                return  # Don't exit; let the app continue running

            current_configs = load_configs(self.DATA_DIR, self.CONFIG_FILE)
            try:
                while self.is_polling.is_set():
                    for conf in current_configs:
                        key = (conf['slave_id'], conf['address'])
                        try:
                            response = self.client.read_holding_registers(address=conf['address'], count=1,
                                                                     device_id=conf['slave_id'])
                            if not response.isError():
                                value = response.registers[0]
                                # Set slave value to TCP Server
                                self.context[0].setValues(3, conf['slave_id'], [value])
                                # Save slave value to SQLite
                                archive_to_sqlite(self.DATA_DIR, conf['slave_id'], value)

                                logger.info(
                                    f"OK:Slave {conf['slave_id']} Register {conf['address']}: {value}")
                            else:
                                self.context[0].setValues(3, conf['slave_id'], [0])
                                logger.warning(
                                    f"Fail to read:Slave {conf['slave_id']} Register {conf['address']}: {response}")

                            time.sleep(self.polling_period)  # Poll every second
                        except ModbusException as e:
                            self.context[0].setValues(3, conf['slave_id'], [0])
                            logger.error(e)
                            time.sleep(1)  # Poll every second
            except Exception as e:
                # current_configs = load_configs()
                # for conf in current_configs:
                #     context[0].setValues(3, conf['slave_id'], [0])

                logger.critical(e)
                # Continue to next iteration instead of exiting
            finally:
                self.client.close()
                logger.info("Connection closed.")

        self.is_polling.set()
        polling_thread = threading.Thread(target=poll_modbus_rtu, daemon=True)
        polling_thread.start()

        logger.info(f"ModbusRTUDataCollector started polling with polling period = {self.polling_period} sec.")

    def stop_polling(self):
        self.is_polling.clear()

        time.sleep(1)
        logger.info("ModbusRTUDataCollector stopped.")