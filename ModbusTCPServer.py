import asyncio
import logging
import threading
import time

from pymodbus import pymodbus_apply_logging_config

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusDeviceContext,
    ModbusServerContext
)
from pymodbus.server import (
    StartTcpServer,
    ServerStop
)
from pymodbus.framer import FramerType

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
pymodbus_apply_logging_config("INFO")

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

class ModbusTCPServer:
    def __init__(self, ip, port):
        datablock = lambda: ModbusSequentialDataBlock(0x00, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

        context = ModbusDeviceContext(
            # di=datablock(),
            # co=datablock(),
            hr=datablock()
            # ir=datablock(),
        )
        single = True
        self.context = ModbusServerContext(devices=context, single=single)
        self.ip = ip
        self.port = port

    def start(self):
        def run_server_thread():
            StartTcpServer(
                context=self.context,
                address=(self.ip, self.port),
                framer=FramerType.SOCKET
            )

        server_thread = threading.Thread(target=run_server_thread, daemon=True)
        server_thread.start()

        time.sleep(0.5)
        logger.info(f"Modbus TCP server started on {self.ip}:{self.port} in a background thread.")

    def stop(self):
        try:
            ServerStop()
        except RuntimeError as e:
            logger.error(f"RuntimeError: {e}")

        logger.info("Modbus TCP server stopped.")

    def set_register(self, address, value):
        """Example method to modify a holding register."""
        self.context[0].setValues(3, address, [value])

    def get_register(self, address, count=1):
        """Read values from a holding register."""
        return self.context[0].getValues(3, address, count)