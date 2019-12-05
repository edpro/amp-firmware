import os
import sys
from enum import Enum
from glob import glob
from os import path

from serial.tools import list_ports

from tools.common.logger import Logger, LoggedError
from tools.common.system import run_shell, delete_files

ESP_FLASH_BAUD = '921600'


class UartStr(Enum):
    CP210 = 'CP210x'
    CH340 = 'CH340'


logger = Logger("esp")


def _detect_port_win(uart_str: UartStr):
    info_list = list_ports.comports()
    info_list = sorted(info_list, key=lambda i: i.device)
    port = ''
    port_count = 0
    for info in info_list:
        if uart_str.value in info.description:
            logger.trace(info.description)
            port = info.device
            port_count += 1

    if port_count == 0:
        logger.throw("Device not found!")

    if port_count > 1:
        logger.throw("Too many ports found: only one device should be connected.")

    return port


def detect_port(uart_str: UartStr):
    if os.name == "nt":
        return _detect_port_win(uart_str)
    else:
        raise LoggedError("Not supported")


def _find_elf_file(bin_dir: str):
    found_files = glob(f"{bin_dir}/*.elf")
    if len(found_files) == 0:
        logger.error(f"ERROR: elf file not found in '{bin_dir}'")
        exit(-1)
    if len(found_files) > 1:
        logger.error(f"ERROR: more then 1 elf file found in {bin_dir}")
        exit(-1)
    logger.trace(f"elf_file: {found_files[0]}")
    return path.normpath(found_files[0])


def esptool(*args):
    cmd = [sys.executable, '-m', 'esptool']
    cmd.extend(args)
    run_shell(cmd)


def print_esp_info(uart_str: UartStr):
    try:
        port = detect_port(uart_str)
        esptool('--port', port,
                '--chip', 'esp8266',
                '--no-stub',
                'chip_id')
    except LoggedError:
        pass


def flash_firmware(bin_dir: str, uart_str: UartStr):
    success = False
    try:
        port = detect_port(uart_str)
        elf = _find_elf_file(bin_dir)
        delete_files(bin_dir, '*.bin')
        esptool('elf2image', elf)
        esptool('image_info', elf + '-0x00000.bin')
        esptool('--port', port,
                '--baud', ESP_FLASH_BAUD,
                '--chip', 'esp8266',
                'write_flash',
                '--flash_freq', '40m',
                '--flash_mode', 'qio',
                '--flash_size', '4MB',
                '0x00000', elf + '-0x00000.bin',
                '0x20000', elf + '-0x20000.bin')
        success = True
        logger.success()
    except LoggedError:
        pass
    return success


def flash_espinit(uart_str: UartStr) -> bool:
    success = False
    try:
        port = detect_port(uart_str)
        esptool('--port', port,
                '--baud', ESP_FLASH_BAUD,
                '--chip', 'esp8266',
                'write_flash',
                '--flash_freq', '40m',
                '--flash_mode', 'qio',
                '--flash_size', '4MB',
                '0x3fc000', './images/esp/esp_init_data_default.bin',
                '0x7E000', './images/esp/blank.bin')
        success = True
        logger.success()
    except LoggedError:
        pass
    return success
