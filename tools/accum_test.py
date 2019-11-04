# noinspection PyMethodParameters
import time

from tools.common.logger import LoggedError, Logger
from tools.common.screen import scr_prompt
from tools.devices.rigol_load import RigolLoad

MIN_V = 3.5
MAX_R = 0.2

load = RigolLoad()
logger = Logger("accum_test")


def test_internal_r():
    logger.info("Testing internal resiatance...")

    load.set_input(0)
    time.sleep(0.5)
    v_unload = load.measure_voltage()
    if (v_unload < MIN_V):
        logger.throw(f"Voltage too low: V < {MIN_V}")

    load.set_const_current(0.1)
    load.set_input(1)
    time.sleep(1)
    v_load = load.measure_voltage()
    i_load = load.measure_current()
    load.set_input(0)

    r = (v_unload - v_load) / i_load
    logger.info(f"Internal_R: {r:0.3}")
    if (r > MAX_R):
        logger.throw(f"Intenal resistance it too high: R > {MAX_R}")


def test_current_1():
    pass


def test_current_2():
    pass


def run_loop():
    while True:
        choise = scr_prompt("Connect accumulator. <Enter> - continue, <q> - quit: ")
        if choise == "q":
            break
        try:
            test_internal_r()
            test_current_1()
            test_current_2()
        except LoggedError:
            pass
        except Exception:
            raise


if __name__ == "__main__":
    try:
        load.connect()
        load.reset()
        run_loop()
    except LoggedError:
        exit(1)
    except Exception:
        raise
    finally:
        load.close()
