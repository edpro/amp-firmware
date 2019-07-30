import os

import serial.tools.list_ports

from tools.common.logger import Logger

class DeviceNotFoundError(Exception):
    def __init__(self):
        super().__init__("No port with connected device found.")


class EdproDevice:
    """handles communication with amperia devices (multimeter & powersource)"""

    SERIAL_BAUD = '74880'

    def __init__(self, tag):
        self.logger = Logger(tag)
        self.logger.info("init")
        self.port = ""

    def detect_port_win(self):
        info_list = serial.tools.list_ports.comports()
        if len(info_list) == 0:
            raise DeviceNotFoundError()

        info_list = sorted(info_list, key=lambda i: i.device)
        port = ''
        port_count = 0
        for info in info_list:
            if 'CP210x' in info.description:
                self.logger.trace(info.description)
                port = info.device
                port_count += 1

        if port_count == 0:
            raise DeviceNotFoundError()

        if port_count > 1:
            raise Exception("Too many ports found: only one device should be connected.")

        return port

    @staticmethod
    def detect_port_osx():
        return '/dev/tty.SLAB_USBtoUART'

    def detect_port(self):
        if os.name == "nt":
            return self.detect_port_win()
        else:
            return self.detect_port_osx()

    def connect(self):
        self.logger.info("connecting...")
        port = self.detect_port()


class EdproPS(EdproDevice):
    def __init__(self):
        super().__init__("ps")


class EdproMM(EdproDevice):
    def __init__(self):
        super().__init__("mm")

def main():
    device = EdproPS()
    try:
        device.connect()
    except Exception as e:
        print("ERROR: " + str(e))
        pass


if __name__ == "__main__":
    main()
