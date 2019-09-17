import time
from typing import Tuple, Optional

from tools.common.logger import Logger, LoggedError
from tools.common.screen import prompt
from tools.common.tests import TestReporter, erel, eabs
from tools.devices.edpro_device import EdproPS
from tools.devices.rigol_meter import RigolMeter, RigolMode

logger = Logger("ps_test")

CIRCUIT_R = 5.6 + 1.0

VDC_REL = 0.02
VDC_ZERO_ABS = 0.04
VDC_STEP_ABS = 0.05

VAC_REL = 0.03
VAC_STEP_ABS = 0.05
VAC_ZERO_ABS = 0.03

ADC_REL = 0.02
ADC_ZERO_ABS = 0.01

AAC_ABS = 0.01

FREQ_REL = 0.01


def check(val: bool, message: str):
    if not val:
        logger.throw(message)


def wait_mode():
    time.sleep(1)


def _init_devices() -> Tuple[EdproPS, RigolMeter]:
    # init rigol
    rigol = RigolMeter()
    rigol.connect()

    # init powersource
    ps = EdproPS()
    ps.connect()
    ps.trace_commands = False
    ps.wait_boot_complete()
    ps.request("devmode")

    # check device is really powersourse
    response = ps.request("i")
    if response.get("name") != "Powersource":
        logger.throw("Invalid device name!")

    return ps, rigol


def _dispose_devices(ps: Optional[EdproPS], ri: Optional[RigolMeter]):
    if ps: ps.close()
    if ri: ri.close()


def test_a_dc(ps: EdproPS, ri: RigolMeter) -> bool:
    t = TestReporter("tast_adc")
    ri.set_mode(RigolMode.VDC_20)
    ps.cmd("mode dc")
    ps.cmd("set l 0")
    wait_mode()

    levels = [0, 2, 4, 6, 10, 20, 30, 40, 50, 0]

    for level in levels:
        step_u = 0.1 * level
        ps.cmd(f"set l {level}")
        time.sleep(0.1)
        ps_val = ps.get_values()
        ri_val = ri.measure_vdc()
        ea = eabs(ps_val.I, ri_val)
        er = erel(ps_val.I, ri_val)
        t.trace(
            f"step: {step_u:0.1f}V | U: {ps_val.U:0.3f} I: {ps_val.I:0.3f} | rigol: {ri_val:0.6f} | abs: {ea:0.6f} | rel: {er * 100:0.2f}%")
        t.expect_abs(ps_val.U, step_u, VDC_STEP_ABS)
        if level == 0:
            t.expect_abs(ri_val, 0, 0.01)
            t.expect_abs(ps_val.I, ri_val, ADC_ZERO_ABS)
        else:
            t.expect_rel(ri_val, ps_val.U / CIRCUIT_R, 0.05)
            t.expect_rel(ps_val.I, ri_val, ADC_REL)

    t.print_result()
    return t.success


def test_a_ac(ps: EdproPS, ri: RigolMeter) -> bool:
    t = TestReporter("tast_aac")
    ri.set_mode(RigolMode.VAC_20)
    ps.cmd("mode ac")
    ps.cmd("set l 0")
    ps.cmd("set f 1000")
    wait_mode()

    levels = [0, 2, 4, 6, 10, 0]

    for level in levels:
        step_u = 0.1 * level
        ps.cmd(f"set l {level}")
        time.sleep(0.25)
        ps_val = ps.get_values()
        ri_val = ri.measure_vac()
        ea = eabs(ps_val.I, ri_val)
        er = erel(ps_val.I, ri_val)
        t.trace(
            f"step: {step_u:0.1f}V | U: {ps_val.U:0.3f} I: {ps_val.I:0.3f} | rigol: {ri_val:0.6f} | abs: {ea:0.6f} | rel: {er * 100:0.2f}%")
        t.expect_abs(ps_val.U, step_u, VAC_STEP_ABS)
        t.expect_abs(ps_val.I, ri_val, AAC_ABS)
        if level > 0:
            t.expect_rel(ri_val, ps_val.U / CIRCUIT_R, 0.1)

    t.print_result()
    return t.success


def ps_run_test():
    ps: Optional[EdproPS] = None
    ri: Optional[RigolMeter] = None
    try:
        ps, ri = _init_devices()

        choise = prompt("Connect Rigol to Powersource output. <Enter> - continue, <s> - skip: ")
        if choise == "":
            while True:
                try:
                    break
                except LoggedError:
                    choise = prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break
                except Exception:
                    raise

        choise = prompt("Connect Rigol to 1Ω resistor. <Enter> - continue, <s> - skip: ")
        if choise == "":
            while True:
                try:
                    check(test_a_dc(ps, ri), "Test failed!")
                    check(test_a_ac(ps, ri), "Test failed!")
                    break
                except LoggedError:
                    choise = prompt("<Enter> - continue, <r> - retry: ")
                    if choise == "":
                        break
                except Exception:
                    raise

    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        _dispose_devices(ps, ri)


def _run():
    ps: Optional[EdproPS] = None
    ri: Optional[RigolMeter] = None
    try:
        ps, ri = _init_devices()
        # check(test_v_dc(ps, ri), "Test Failed!")
        # check(test_v_ac(ps, ri), "Test Failed!")
        # check(test_freq(ps, ri), "Test Failed!")
        # test_a_dc(ps, ri)
        test_a_ac(ps, ri)

    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        _dispose_devices(ps, ri)


if __name__ == "__main__":
    _run()
