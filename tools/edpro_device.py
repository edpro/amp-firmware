import os
import threading
import time
from typing import Optional, Dict

import serial
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
        self._serial: Optional[serial.Serial] = None
        self._rx_thread: Optional[threading.Thread] = None
        self._rx_alive: bool = False
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

    def _reader_proc(self):
        try:
            while self._rx_alive:
                data = self._serial.readline()
                if data:
                    line = decode_device_line(data)
                    print_device_line(line)
                    if line.startswith(":"):
                        with self._lock:
                            self._response = line
        except serial.SerialException:
            self._rx_alive = False
            raise

    def connect(self):
        self.logger.info("connect")
        self._rx_alive = True
        self._port = self._detect_port()

        self._serial = serial.serial_for_url(self._port, 74880,
                                             parity="N",
                                             stopbits=1,
                                             rtscts=False,
                                             xonxoff=False,
                                             do_not_open=True)

        # self._serial.rts = False
        # self._serial.dtr = False
        self._serial.open()
        self._start_reader()

    def _start_reader(self):
        self.logger.trace("start reader")
        self._rx_alive = True
        self._rx_thread = threading.Thread(target=self._reader_proc, name='rx')
        self._rx_thread.daemon = True
        self._rx_thread.start()

    def _stop_reader(self):
        self.logger.trace("stop reader")
        self._rx_alive = False
        self._rx_thread.join()

    def disconnect(self):
        self.logger.info("disconnect")
        if self._serial is None:
            return
        self._stop_reader()
        self._serial.close()
        self._serial = None

    def run_command(self, cmd):
        self.logger.info(f"<- '{cmd}'")

        self._serial.write("\n\n\n\n".encode())
        self._serial.write(f"{cmd}\n".encode())

        self._serial.flush()
        pass

    def run_request(self, cmd):
        self.logger.info(f"<- '{cmd}'")

        with self._lock:
            self._response = None

        self._serial.write("\n\n\n\n".encode())
        self._serial.write(f"{cmd}\n".encode())

        self._serial.flush()

        time_start = time.time()
        timeout = 4
        response = {}

        while True:
            time.sleep(0.1)
            if self._response is None:
                elapsed = time.time() - time_start
                if elapsed > timeout:
                    raise Exception("Request timeout!")
                continue
            with self._lock:
                assert isinstance(self._response, str)
                response = decode_response(self._response)
                break

        self.logger.info(f"-> {str(response)}")


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
        time.sleep(2)
        device.run_request("i")
    except Exception as e:
        print("ERROR: " + str(e))

    time.sleep(1)
    device.disconnect()


if __name__ == "__main__":
    main()
