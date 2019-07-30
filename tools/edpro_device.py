import os
import threading
import time

from serial import Serial, PARITY_NONE, SerialException
from serial.tools import list_ports

from tools.common.logger import Logger, Colors


class DeviceNotFoundError(Exception):
    def __init__(self):
        super().__init__("No port with connected device found.")


def decode_device_line(data: bytearray):
    line = data.decode("utf-8")
    line = line.replace("\r", "")
    line = line.replace("\n", "")
    return line


def print_device_line(line: str):
    if line == "":
        return
    color = Colors.GRAY
    line = line.strip()
    if line.startswith('W '):
        color = Colors.YELLOW
    elif line.startswith('E '):
        color = Colors.RED
    print(f"     {color}{line}{Colors.RESET}")


class EdproDevice:
    """handles communication with amperia devices (multimeter & powersource)"""

    def __init__(self, tag):
        self.logger = Logger(tag)
        self.logger.info("init")
        self._port = None
        self._serial = None
        self._alive = False

    def _detect_port_win(self):
        info_list = list_ports.comports()
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
    def _detect_port_osx():
        return '/dev/tty.SLAB_USBtoUART'

    def _detect_port(self):
        if os.name == "nt":
            return self._detect_port_win()
        else:
            return self._detect_port_osx()

    def _reader(self):
        try:
            while self._alive:
                data = self._serial.readline()
                if data:
                    line = decode_device_line(data)
                    print_device_line(line)
        except SerialException:
            self._alive = False
            raise

    def _start_reader(self):
        self.logger.trace("start reader")
        # self._reader()
        self.receiver_thread = threading.Thread(target=self._reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        # self.receiver_thread.join()

    def connect(self):
        self.logger.info("connect")
        self._alive = True
        self._port = self._detect_port()
        self._serial = Serial()
        self._serial.port = self._port
        self._serial.baudrate = 74880
        self._serial.timeout = 1
        self._serial.bytesize = 8
        self._serial.parity = PARITY_NONE
        self._serial.stopbits = 1
        self._serial.xonxoff = 0
        self._serial.rtscts = 0
        self._serial.open()
        self._serial.write("\n\n\n\n".encode())
        self._start_reader()

    def run_command(self, cmd):
        self.logger.info(f"run command: '{cmd}'")
        self._serial.write(f"{cmd}\n".encode())
        pass

    def disconnect(self):
        self.logger.info("disconnect")
        self._alive = False
        if self._serial is None:
            return
        self._serial.close()
        self._serial = None


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

    time.sleep(2)
    device.run_command("i")
    input("Press Enter to continue...\n")
    device.disconnect()


if __name__ == "__main__":
    main()
