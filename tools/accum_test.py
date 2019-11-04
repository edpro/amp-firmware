# noinspection PyMethodParameters

from tools.common.logger import LoggedError, Logger
from tools.common.screen import scr_prompt
from tools.devices.rigol_load import RigolLoad

MIN_V = 4.5

load = RigolLoad()
logger = Logger("accum_test")


def test_internal_r():
    logger.info("Testing internal resiatance...")
    v = load.measure_voltage()
    if (v < MIN_V):
        logger.throw(f"Voltage too low: V < {MIN_V}")


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
