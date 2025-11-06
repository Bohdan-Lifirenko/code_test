import logging
import os
import sqlite3
import threading
import time
from datetime import date
from datetime import datetime

from pymodbus import pymodbus_apply_logging_config, ModbusException
from pymodbus.client import ModbusSerialClient
from db_communication import load_slaves_list, archive_to_sqlite, load_rtu_serial_params

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
            polling_period,
            slaves_config,
            context,
            data_dir,
            rtu_serial_params_dict
    ):
        self.polling_period = polling_period
        self.rtu_serial_params_dict = rtu_serial_params_dict
        self.slaves_config = slaves_config

        self.context = context

        self.client = ModbusSerialClient(
            port=rtu_serial_params_dict["convertor_port"],          # Or '/dev/ttyUSB0' on Linux/macOS
            baudrate=rtu_serial_params_dict["baudrate"],        # Match your slave's baud rate
            bytesize=rtu_serial_params_dict["bytesize"],
            parity=rtu_serial_params_dict["parity"],           # 'N' for none, 'E' for even, 'O' for odd
            stopbits=rtu_serial_params_dict["stopbits"],
            timeout=rtu_serial_params_dict["stopbits"],             # In seconds
            retries=rtu_serial_params_dict["polling_period"]
        )

        self.data_dir = data_dir

        self.is_polling = threading.Event()
        self.need_to_update_slaves_list = threading.Event()
        self.need_to_update_rtu_serial_params = threading.Event()


    def start_polling(self):
        def poll_modbus_rtu():
            if self.client.connect():
                logger.info("Connected successfully!")
            else:
                logging.error("Failed to connect. Check port, wiring, or parameters.")
                return  # Don't exit; let the app continue running

            current_configs = self.slaves_config

            try:
                while self.is_polling.is_set():
                    if self.need_to_update_slaves_list.is_set():
                        current_configs = self.slaves_config
                        self.need_to_update_slaves_list.clear()

                    for conf in current_configs:
                        key = (conf['slave_id'], conf['address'])
                        logger.info(
                            f"Polling slave {conf['slave_id']}, register {conf['address']}")
                        try:
                            response = self.client.read_holding_registers(address=conf['address'], count=1,
                                                                     device_id=conf['slave_id'])
                            if not response.isError():
                                value = response.registers[0]
                                # Set slave value to TCP Server
                                self.context[0].setValues(3, conf['slave_id'], [value])
                                # Save slave value to SQLite
                                archive_to_sqlite(self.data_dir, conf['slave_id'], value)

                                logger.info(
                                    f"OK: {value}")
                            else:
                                self.context[0].setValues(3, conf['slave_id'], [0])
                                archive_to_sqlite(self.data_dir, conf['slave_id'], 0)
                                logger.warning(
                                    f"Fail to read:Slave {conf['slave_id']} Register {conf['address']}: {response}")

                            time.sleep(self.polling_period)  # Poll every second
                        except ModbusException as e:
                            self.context[0].setValues(3, conf['slave_id'], [0])
                            archive_to_sqlite(self.data_dir, conf['slave_id'], 0)

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

    def change_slaves_config(self, new_config):
        self.slaves_config = new_config
        self.need_to_update_slaves_list.set()

    def change_rtu_serial_params(self, new_rtu_serial_params_dict):
        self.rtu_serial_params_dict = new_rtu_serial_params_dict
        self.need_to_update_slaves_list.set()

        self.client = ModbusSerialClient(
            port=new_rtu_serial_params_dict["convertor_port"],  # Or '/dev/ttyUSB0' on Linux/macOS
            baudrate=new_rtu_serial_params_dict["baudrate"],  # Match your slave's baud rate
            bytesize=new_rtu_serial_params_dict["bytesize"],
            parity=new_rtu_serial_params_dict["parity"],  # 'N' for none, 'E' for even, 'O' for odd
            stopbits=new_rtu_serial_params_dict["stopbits"],
            timeout=new_rtu_serial_params_dict["stopbits"],  # In seconds
            retries=new_rtu_serial_params_dict["polling_period"]
        )

    def change_rtu_serial_params(
            self,
            params_dict
    ):
        self.convertor_port = params_dict["convertor_port"]
        self.baudrate = params_dict["baudrate"]
        self.bytesize = params_dict["bytesize"]
        self.parity = params_dict["parity"]
        self.stopbits = params_dict["stopbits"]
        self.polling_period = params_dict["polling_period"]