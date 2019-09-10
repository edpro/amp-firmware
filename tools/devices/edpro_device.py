import threading
import time
from typing import Optional, Dict, NamedTuple

import serial

from tools.common.logger import Logger, LoggedError
from tools.common.screen import Colors, print_color
from tools.common.utils import detect_port


def decode_device_line(data: bytes) -> str:
    try:
        line = data.decode("utf-8")
        line = line.replace("\r", "")
        line = line.replace("\n", "")
        return line
    except UnicodeDecodeError:
        data = data.replace(b"\r", b"")
        data = data.replace(b"\n", b"")
        return str(data)


def decode_response(raw: str) -> Dict[str, str]:
    pairs = raw.split(" ")
    result = {}
    for pair in pairs:
        parts = pair.split("=")
        if len(parts) == 2:
            result[parts[0]] = parts[1]
    return result


class EInfoResult(NamedTuple):
    name: str
    version: str


class EdproDevice:
    """handles communication with amperia devices (multimeter & powersource)"""

    def __init__(self, tag):
        self.log_mode = False
        self.tag = tag
        self.logger = Logger(tag)
        self.trace_commands = True
        self._port: Optional[str] = None
        self._serial: Optional[serial.Serial] = None
        self._rx_thread: Optional[threading.Thread] = None
        self._rx_alive: bool = False
        self._response: Optional[str] = None
        self._lock = threading.Lock()
        self._uart_written = False

    def _print_device_line(self, line: str):
        if line == "":
            return

        color = Colors.GRAY

        if self.log_mode:
            if line.startswith('D '):
                line = line[2:]
                color = Colors.GRAY
            if line.startswith('I '):
                line = line[2:]
                color = Colors.LIGHT_BLUE
            if line.startswith('W '):
                line = line[2:]
                color = Colors.YELLOW
            elif line.startswith('E '):
                line = line[2:]
                color = Colors.RED
            print(f"[{self.tag}] {color}░ {line.strip()}{Colors.RESET}")
        else:
            if line.startswith('W '):
                color = Colors.YELLOW
            elif line.startswith('E '):
                color = Colors.RED
            print(f"[{self.tag}] {color}░ {line.strip()}{Colors.RESET}")

    def _reader_proc(self):
        try:
            while self._rx_alive:
                data = self._serial.readline()
                if data and self._rx_alive:
                    line = decode_device_line(data)
                    self._print_device_line(line)
                    if line.startswith(":"):
                        with self._lock:
                            self._response = line
        except Exception as e:
            self.logger.error(e)
            self._rx_alive = False
            raise

    def connect(self, reboot: bool = True):
        self.logger.info("connect")
        self._rx_alive = True
        self._port = detect_port()

        self._serial = serial.serial_for_url(self._port, 74880,
                                             parity="N",
                                             stopbits=1,
                                             dsrdtr=False,
                                             rtscts=False,
                                             xonxoff=False,
                                             do_not_open=True,
                                             timeout=1)

        if reboot:
            self._serial.dtr = False
            self._serial.rts = True
        else:
            self._serial.dtr = False
            self._serial.rts = False

        # open
        try:
            self._serial.open()
        except Exception as e:
            self.logger.throw(e)

        if reboot:
            time.sleep(0.1)
            self._serial.dtr = True
            time.sleep(0.1)
            self._serial.rts = False

        # start reading thread
        self._start_reader()

    def _start_reader(self):
        # self.logger.trace("starting reader")
        self._rx_alive = True
        self._rx_thread = threading.Thread(target=self._reader_proc, name='rx')
        self._rx_thread.daemon = True
        self._rx_thread.start()

    def _stop_reader(self):
        # self.logger.trace("stopping reader...")
        self._rx_alive = False
        if self._rx_thread:
            self._rx_thread.join()

    def close(self):
        self.logger.info("disconnect")
        if self._serial is None:
            return
        self._stop_reader()

        # to prevent device being in reset state after serial.Close()
        # self._serial.rts = False
        self._serial.close()
        self._serial = None

    def _fix_uart_issue(self):
        if self._uart_written:
            return
        for i in range(0, 8):
            self._serial.write(b"\n")
        self._uart_written = True

    def request(self, cmd: str, wait: bool = True, trace: bool = True) -> Dict[str, str]:
        if self.trace_commands and trace:
            self.logger.trace(f"<- '{cmd}'")

        with self._lock:
            self._response = None

        self._fix_uart_issue()
        self._serial.write(f"{cmd}\n".encode())
        self._serial.flush()

        if not wait:
            return {}

        time_start = time.time()
        timeout = 4
        response = {}

        while True:
            time.sleep(0.1)
            if self._response is None:
                elapsed = time.time() - time_start
                if elapsed > timeout:
                    self.logger.throw("Request timeout!")
                continue
            with self._lock:
                assert isinstance(self._response, str)
                response = decode_response(self._response)
                break

        if self.trace_commands and trace:
            self.logger.trace(f"-> {str(response)}")
        return response

    def cmd(self, cmd: str):
        r = self.request(cmd)
        if r.get("success") != "1":
            self.logger.throw("command failed")

    def cmd_save_conf(self):
        self.cmd("conf s")

    def wait_boot_complete(self):
        self.logger.info("waiting for boot complete...")

        time_start = time.time()
        timeout = 4

        while True:
            time.sleep(0.1)
            if self._response is None:
                elapsed = time.time() - time_start
                if elapsed > timeout:
                    self.logger.throw("Waiting timeout!")
                continue
            with self._lock:
                assert isinstance(self._response, str)
                response = decode_response(self._response)

            self.logger.trace(f"-> {response}")
            if response.get("init") == "0":
                self.logger.throw("Device init failed!")
            if response.get("init") == "1":
                break

        self.logger.info("ready")

    def show_log(self):
        try:
            self.log_mode = True
            self.connect(reboot=False)
            print_color("\n<?> - help, <q> - exit", Colors.GREEN)
            while True:
                cmd = input("")
                if cmd == "q":
                    break
                try:
                    self.request(cmd, wait=False, trace=False)
                except LoggedError:
                    pass
            self.close()
        except LoggedError:
            self.close()
        except KeyboardInterrupt:
            self.close()
        except Exception:
            self.close()
            raise

    def request_info(self) -> EInfoResult:
        r = self.request("i")
        return EInfoResult(name=r["name"], version=r["version"])


class PSValues:
    def __init__(self, U: float = 0, I: float = 0):
        self.U: float = U
        self.I: float = I


class EdproPS(EdproDevice):
    def __init__(self):
        super().__init__("ps")

    def request_values(self) -> PSValues:
        r = self.request("v")
        if r.get("success") != "1":
            self.logger.throw("Request not succeed!")
        return PSValues(float(r["U"]), float(r["I"]))


class EdproMM(EdproDevice):
    def __init__(self):
        super().__init__("mm")

    def request_mode(self) -> str:
        response = self.request("mode")
        return response["mode"]

    def request_value(self) -> float:
        response = self.request("v")
        return float(response["value"])


def test():
    device = EdproPS()
    device.connect()
    device.wait_boot_complete()
    device.request("devmode")
    device.request("i")
    device.close()


if __name__ == "__main__":
    try:
        test()
    except LoggedError:
        pass
    except Exception:
        raise
