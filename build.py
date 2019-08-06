#!/usr/bin/env python3

import sys
import os
import subprocess
import serial.tools.list_ports

from os import path
from glob import glob

#
# env
#

OS_WINDOWS = os.name == 'nt'
OUT_DIR = 'out'
FLASH_BAUD = '921600'
SERIAL_BAUD = '74880'
SERIAL_EXIT = '27'
PORT = ''

if not os.path.isfile('build.conf.py'):
    f = open("build.conf.py", "w")
    f.write("# PORT = 'COM1'\n")
    f.write("# PORT = 'COM2'\n")
    f.write("# PORT = 'COM3'\n")
    f.write("# PORT = 'COM4'\n")
    f.write("# PORT = 'COM5'\n")
    f.write("# PORT = 'COM6'\n")
    f.write("# PORT = 'COM7'\n")
    f.write("# PORT = 'COM8'\n")
    f.write("# PORT = 'COM9'\n")
    f.write("\n")
    f.write("# FLASH_BAUD = '115200'\n")
    f.write("# FLASH_BAUD = '256000'\n")
    f.write("# FLASH_BAUD = '512000'\n")
    f.write("# FLASH_BAUD = '921600'\n")
    f.close()

exec(open('build.conf.py').read())

#
# helpers
#

if OS_WINDOWS:
    import ctypes

    # enable ANSI colors in Win10 console
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

C_DBG = '\033[37m'
C_INFO = '\033[94m'
C_WARN = '\033[33m'
C_ERR = '\033[1;41m'
C_HEAD = '\033[35m'
C_END = '\033[0m'


def log(msg):
    print(C_INFO + msg + C_END)


def log_h(msg):
    print(C_HEAD + msg + C_END)


def log_w(msg):
    print(C_WARN + msg + C_END)


def log_e(msg):
    print(C_ERR + msg + C_END)


def print_env(var_name):
    log_w('{:<12} = {}'.format(var_name, eval(var_name)))


def print_cmd(args_list):
    log('> ' + ' '.join(args_list))


def system(args, cwd=None):
    """
    :type args: list
    :type cwd: string
    """
    print_cmd(args)
    sys.stdout.flush()
    retcode = subprocess.call(args, cwd=cwd)
    if retcode != 0:
        log_e('FAILED')
        exit(retcode)


def esptool(*args):
    cmd = [sys.executable, '-m', 'esptool']
    cmd.extend(args)
    system(cmd)


def delete_files(pdir, mask):
    for file in glob(path.join(pdir, mask)):
        os.remove(file)


#
# tasks
#


def elf_file():
    found_files = glob(OUT_DIR + "/*.elf")
    if len(found_files) == 0:
        log_e(f"ERROR: elf file not found in {OUT_DIR}")
        exit(-1)
    if len(found_files) > 1:
        log_e(f"ERROR: more then 1 elf file found in {OUT_DIR}")
        exit(-1)
    log(f"elf_file: {found_files[0]}")
    return path.normpath(found_files[0])


def init():
    esptool('--port', PORT,
            '--baud', FLASH_BAUD,
            '--chip', 'esp8266',
            'write_flash',
            '--flash_freq', '40m',
            '--flash_mode', 'qio',
            '--flash_size', '4MB',
            '0x3fc000', './images/esp/esp_init_data_default.bin',
            '0x7E000', './images/esp/blank.bin')


def elf2bin():
    elf = elf_file()
    delete_files(OUT_DIR, '*.bin')
    esptool('elf2image', elf)
    esptool('image_info', elf + '-0x00000.bin')


def flush():
    elf = elf_file()
    delete_files(OUT_DIR, '*.bin')
    esptool('elf2image', elf)
    esptool('image_info', elf + '-0x00000.bin')
    esptool('--port', PORT,
            '--baud', FLASH_BAUD,
            '--chip', 'esp8266',
            'write_flash',
            '--flash_freq', '40m',
            '--flash_mode', 'qio',
            '--flash_size', '4MB',
            '0x00000', elf + '-0x00000.bin',
            '0x20000', elf + '-0x20000.bin')


def erase():
    esptool('--port', PORT,
            '--baud', FLASH_BAUD,
            '--chip', 'esp8266',
            'erase_flash')


def print_device_log(line):
    if line.startswith('D '):
        sys.stdout.write(C_DBG + line + C_END)
    elif line.startswith('I '):
        sys.stdout.write(C_INFO + line + C_END)
    elif line.startswith('W '):
        sys.stdout.write(C_WARN + line + C_END)
    elif line.startswith('E '):
        sys.stdout.write(C_ERR + line + C_END)
    else:
        sys.stdout.write(line)


def connect():
    call_params = [sys.executable, '-m', 'serial.tools.miniterm',
                   '--exit-char', SERIAL_EXIT,
                   '--rts', '0',
                   '--dtr', '0',
                   PORT, SERIAL_BAUD]
    print_cmd(call_params)
    sys.stdout.flush()
    p = subprocess.Popen(call_params, stdout=subprocess.PIPE)
    while True:
        output = p.stdout.readline()
        if output == b'':
            break
        line = output.decode("utf-8")
        print_device_log(line)
    sys.stdout.flush()


def check_env():
    esptool('version')


def detect_port_win():
    info_list = serial.tools.list_ports.comports()
    if len(info_list) == 0:
        return ''
    info_list = sorted(info_list, key=lambda i: i.device)
    port = ''
    port_count = 0
    for info in info_list:
        if 'CP210x' in info.description:
            print(': ' + info.description)
            port = info.device
            port_count += 1

    if port_count > 1:
        log_e("Error: Too many ports found")
        exit(1)

    return port


def detect_port_osx():
    return '/dev/tty.SLAB_USBtoUART'


def print_usages():
    log("Usage:")
    print("build connect [PORT]")
    print("build deploy [elf_dir]")
    print("build erase")
    print("build elf2bin")
    print("build init")


#
# args
#

if len(sys.argv) == 1:
    print_usages()
    exit(0)

if sys.argv[1] == "elf2bin":
    if len(sys.argv) > 2:
        OUT_DIR = path.normpath(sys.argv[2])
    print_env('OUT_DIR')
    check_env()
    elf2bin()
    exit(0)

if PORT == '':
    if OS_WINDOWS:
        PORT = detect_port_win()
    else:
        PORT = detect_port_osx()

if PORT == '':
    log_e("ERROR: Serial port not found")
    exit(-1)

if sys.argv[1] == "init":
    OUT_DIR = './bin'
    print_env('OUT_DIR')
    print_env('FLASH_BAUD')
    print_env('PORT')
    check_env()
    init()
    exit(0)

if sys.argv[1] == "erase":
    print_env('FLASH_BAUD')
    print_env('PORT')
    check_env()
    erase()
    exit(0)

if sys.argv[1] == "deploy":
    if len(sys.argv) > 2:
        OUT_DIR = path.normpath(sys.argv[2])
    print_env('OUT_DIR')
    print_env('FLASH_BAUD')
    print_env('PORT')
    check_env()
    flush()
    connect()
    exit(0)

if sys.argv[1] == "connect":
    if len(sys.argv) > 2:
        PORT = sys.argv[2]
    print_env('PORT')
    check_env()
    connect()
    exit(0)
