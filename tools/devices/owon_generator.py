import time
from array import array
from typing import Optional

import usb.util

from tools.common.logger import Logger, LoggedError

logger = Logger("gen")

READ_TIMEOUT = 5000
INTERFACE_NUM = 0
BUF_SIZE = 1024


def usb_find_reader(interface):
    return usb.util.find_descriptor(
        interface,
        # match the first IN endpoint
        custom_match=(
            lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) ==
            usb.util.ENDPOINT_IN)
    )


def usb_find_writer(interface):
    return usb.util.find_descriptor(
        interface,
        # match the first OUT endpoint
        custom_match=(
            lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress) ==
            usb.util.ENDPOINT_OUT)
    )


class USBSource:
    def __init__(self):
        self._device: Optional[usb.core.Device] = None
        self._reader = None
        self._writer = None

    def connect(self):
        logger.info("connect")
        it = usb.core.find(find_all=True, idVendor=0x5345, idProduct=0x1234)
        device = next(it)
        if device is None:
            logger.throw("Device not found!")

        logger.trace(f'found: {device.serial_number}')

        usb.util.claim_interface(device, INTERFACE_NUM)
        device.set_configuration()
        cfg = device.get_active_configuration()
        intf = cfg[(0, 0)]
        self._device = device
        self._reader = usb_find_reader(intf)
        self._writer = usb_find_writer(intf)

    def write(self, cmd: str):
        logger.trace(f"<- {cmd}")
        self._writer.write(cmd.encode())
        self._writer.write(b"\n")

    def read(self, length) -> str:
        rec_arr: array = self._reader.read(length, READ_TIMEOUT)
        bb: bytearray = rec_arr.tobytes()
        text = bb.decode()
        if text.endswith("\n->\n"):
            text = text[0:-4]
        logger.trace(f"-> {text}")
        return text

    def close(self):
        logger.info("disconnect")
        usb.util.release_interface(self._device, INTERFACE_NUM)

    # def set_output_off(self):
    #     self.write()

    def set_ac(self, amp: int, freq: int):
        self.write(f":FUNC:SINE")
        self.write(f":FUNC:SINE:FREQ {freq}")
        self.write(f":FUNC:SINE:AMPL {amp}")


def _run():
    dev = USBSource()
    dev.connect()
    # dev.write("*RST")
    dev.write("*IDN?")
    dev.read(BUF_SIZE)
    time.sleep(1)
    dev.set_ac(2, 500)
    dev.close()


if __name__ == '__main__':
    try:
        _run()
    except LoggedError:
        pass
    except Exception:
        raise
