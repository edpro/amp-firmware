import os
import threading
import time
from typing import Optional, Dict

from serial import Serial, PARITY_NONE, SerialException
from serial.tools import list_ports
from tools.common.logger import Logger, Colors


class DeviceNotFoundError(Exception):
    def __init__(self):
        super().__init__("No port with connected device found.")


def decode_device_line(data: bytes) -> str:
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


def decode_response(raw: str) -> Dict[str, str]:
    pairs = raw.split(" ")
    result = {}
    for pair in pairs:
        parts = pair.split("=")
        if len(parts) == 2:
            result[parts[0]] = parts[1]
    return result


class EdproDevice:
    """handles communication with amperia devices (multimeter & powersource)"""

    def __init__(self, tag):
        self.logger = Logger(tag)
        self.logger.info("init")
        self._port: Optional[str] = None
        self._serial: Optional[Serial] = None
        self._alive: bool = False
        self._response: Optional[str] = ""
        self._lock = threading.Lock()

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
                    if line.startswith(":"):
                        with self._lock:
                            self._response = line
        except SerialException:
            self._alive = False
            raise

    def _start_reader(self):
        self.logger.trace("start reader")
        self.receiver_thread = threading.Thread(target=self._reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def connect(self):
        self.logger.info("connect")
        self._alive = True
        self._port = self._detect_port()
        self._serial = Serial()
        self._serial.port = self._port
        self._serial.baudrate = 74880
        self._serial.timeout = 1
        self._serial.bytesize = 8
        self._serial.stopbits = 1
        self._serial.parity = PARITY_NONE
        self._serial.open()
        self._serial.write("\n\n\n\n".encode())
        self._start_reader()

    def run_command(self, cmd):
        self.logger.info(f"<- '{cmd}'")
        self._serial.write(f"{cmd}\n".encode())
        pass

    def run_request(self, cmd):
        self.logger.info(f"<- '{cmd}'")

        with self._lock:
            self._response = None

        self._serial.write(f"{cmd}\n".encode())

        time_start = time.time()
        timeout = 4
        response = {}

        while True:
            time.sleep(0.1)
            if self._response == None:
                elapsed = time.time() - time_start
                if elapsed > timeout:
                    raise Exception("Request timeout!")
                continue
            with self._lock:
                assert isinstance(self._response, str)
                response = decode_response(self._response)
                break

        self.logger.info(f"-> '{response}'")

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
    device.run_request("i")
    input("Press Enter to continue...\n")
    device.disconnect()


if __name__ == "__main__":
    main()
