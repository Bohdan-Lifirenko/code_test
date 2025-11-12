import os
import sqlite3
import threading
import time

from app.flask_server import run_server, add_variable_to_server_config
from modbus.modbus_tcp_server import ModbusTCPServer
from modbus.modbus_rtu_collector import ModbusRTUCollector
from modbus.fake_tcp_client import FakeTCPClient
from db_communication import load_slaves_list, create_modbus_rtu_config, load_rtu_serial_params, update_servers_config, \
    get_servers_config, create_servers_config, create_slaves_list

from flask import send_from_directory, Flask, render_template, request, redirect, url_for
from logging_setup import setup_logging
import logging
logger = logging.getLogger(__name__)  # __name__ is the module's name, e.g., "modbus.client"

# Get absolute path to the folder where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Setting log folder
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LAST_LOG_FILE = os.path.join(LOGS_DIR, "app.log")

setup_logging(log_level='INFO', log_file_path=LAST_LOG_FILE)
logger.warning("Starting program.")
time.sleep(3)

#Setting data folder
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
# Database file inside that folder
CONFIG_FILE = os.path.join(DATA_DIR, "config.sqlite")
logger.info(f"Path to config file: {CONFIG_FILE}")

create_modbus_rtu_config(CONFIG_FILE)
create_servers_config(CONFIG_FILE)
create_slaves_list(CONFIG_FILE)

network_config_dict = get_servers_config(CONFIG_FILE)

server = ModbusTCPServer(ip=network_config_dict["modbus_ip"], port=network_config_dict["modbus_port"])
server.start()

client = ModbusRTUCollector(
    polling_period=1,
    slaves_config=load_slaves_list(DATA_DIR, CONFIG_FILE),
    context=server.context,
    data_dir=DATA_DIR,
    rtu_serial_params_dict=load_rtu_serial_params(CONFIG_FILE)
)
#client.start_polling()

face_client = FakeTCPClient(
    polling_period=1,
    slaves_config=load_slaves_list(DATA_DIR, CONFIG_FILE),
    data_dir=DATA_DIR
)
face_client.start_polling()

# Example usage in a program with other tasks:
if __name__ == "__main__":
    add_variable_to_server_config("DATA_DIR", DATA_DIR)
    add_variable_to_server_config("CONFIG_FILE", CONFIG_FILE)
    add_variable_to_server_config("LOGS_DIR", LOGS_DIR)
    add_variable_to_server_config("LAST_LOG_FILE", LAST_LOG_FILE)

    run_server(
        ip=network_config_dict["flask_ip"],
        port=network_config_dict["flask_port"]
    )



    # Запускаємо Flask в іншому потоці (для розробки; у продакшені використовуйте gunicorn)
    # flask_thread = threading.Thread(target=lambda: app.run(host=network_config_dict["flask_ip"], port=network_config_dict["flask_port"]))
    # flask_thread.start()

    # server = ModbusTCPServer(ip='127.0.0.1', port=5020)
    # server.start()
    #
    # client = ModbusTCPClient(
    #     convertor_port='COM7',
    #     baudrate=9600,  # Match your slave's baud rate
    #     bytesize=8,
    #     parity='N',  # 'N' for none, 'E' for even, 'O' for odd
    #     stopbits=1,
    #     polling_period=1,
    #     DATA_DIR=DATA_DIR,
    #     CONFIG_FILE=CONFIG_FILE,
    #     context=server.context
    # )
    # client.start_polling()

    while True:
        print("Run")
        time.sleep(2)

    # # Simulate other tasks running in the main thread
    # try:
    #     for i in range(10):
    #         print(f"Main program task: {i}")
    #         time.sleep(1)
    #
    #     # Stop and restart example
    #     server.stop()
    #     client.stop_polling()
    #     time.sleep(2)
    #
    #     # Run a bit more
    #     for i in range(5):
    #         print(f"Main program task after restart: {i}")
    #         time.sleep(1)
    # finally:
    #     server.stop()