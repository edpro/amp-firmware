from array import array
from typing import Optional

import usb.util

from tools.common.logger import Logger, LoggedError

logger = Logger("ow_power")

READ_TIMEOUT = 5000
INTERFACE_NUM = 0
BUF_SIZE = 1024


def usb_find_reader(interface):
    return usb.util.find_descriptor(
        interface,
        custom_match=lambda e:
        usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
    )


def usb_find_writer(interface):
    return usb.util.find_descriptor(
        interface,
        custom_match=lambda e:
        usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
    )


class OwonPower:
    """
    handles communication with OWON ODP3031 programmable power supply
    http://files.owon.com.cn/probook/ODP3031_Power_Supply_USER_MANUAL.pdf
    """

    def __init__(self):
        self._device: Optional[usb.core.Device] = None
        self._reader = None
        self._writer = None

    def connect(self):

        logger.info("connect")

        def matcher(d):
            return d.idVendor == 0x5345 \
                   and d.idProduct == 0x1234 \
                   and d.serial_number.startswith("ODP3031")

        found_list = list(usb.core.find(find_all=True, custom_match=matcher))

        for d in found_list:
            logger.trace(f'found: {d.manufacturer} {d.product} {d.serial_number}')

        if len(found_list) == 0:
            logger.throw("Cannot find device: OWON-ODP3031")
        elif len(found_list) > 1:
            logger.throw("Too much devices found!")

        device = found_list[0]
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

    def read(self, length) -> str:
        rec_arr: array = self._reader.read(length, READ_TIMEOUT)
        bb: bytearray = rec_arr.tobytes()
        text = bb.decode()
        logger.trace(f"-> {text}")
        return text

    def close(self):
        logger.info("disconnect")
        if self._device != None:
            usb.util.release_interface(self._device, INTERFACE_NUM)

    def get_info(self):
        self.write(f"*IDN?")
        self.read(BUF_SIZE)


def _run():
    dev = OwonPower()
    dev.connect()
    dev.get_info()
    # dev.reset()
    # dev.set_ac(2, 500)
    # dev.set_dc(3)
    # dev.set_on()
    dev.close()


if __name__ == '__main__':
    try:
        _run()
    except LoggedError:
        pass
    except Exception:
        raise