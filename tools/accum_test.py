# noinspection PyMethodParameters
import time

from tools.common.logger import LoggedError, Logger
from tools.common.screen import scr_prompt
from tools.devices.rigol_load import RigolLoad

MIN_V = 3.5
MAX_R = 0.15

load = RigolLoad()
logger = Logger("accum_test")


def test_internal_r():
    logger.info("Testing internal resistance")

    load.set_input(0)
    time.sleep(0.25)
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


def test_current_pulse(amperes: float, milliseconds: float, expected: bool):
    logger.info(f"Testing ipulse: {amperes}A, {milliseconds}ms")

    load.set_input(0)
    time.sleep(0.25)
    v1 = load.measure_voltage()
    if (v1 < MIN_V):
        logger.throw(f"Voltage too low: V < {MIN_V}")

    load.set_pulse_current(value=amperes, width_ms=milliseconds)
    load.trigger()
    time.sleep(milliseconds / 1000 + 1.0)
    v2 = load.measure_voltage()
    load.set_input(0)

    if expected:
        if (abs(v2 - v1) > 0.1):
            logger.throw(f"Voltage is not recovered")
    else:
        if (abs(v2) > 0.01):
            logger.throw(f"Voltage must not be recovered")


def run_loop():
    while True:
        choise = scr_prompt("Connect accumulator. <Enter> - continue, <q> - quit: ")
        if choise == "q":
            break
        try:
            test_internal_r()
            test_current_pulse(10, 20, False)
            scr_prompt("Reconnect accumulator. <Enter> - continue")
            test_current_pulse(5.5, 1000, True)
            test_current_pulse(10, 0.05, True)
            logger.success("OK!")
        except LoggedError:
            pass


if __name__ == "__main__":
    try:
        load.connect()
        load.reset()
        run_loop()
    except LoggedError:
        exit(1)
    finally:
        load.close()
