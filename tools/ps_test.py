import time
from typing import Tuple, Optional

from tools.common.logger import Logger, LoggedError
from tools.common.screen import prompt
from tools.common.tests import TestRecorder, erel, eabs
from tools.edpro_device import EdproPS
from tools.rigol_device import RigolDevice, RigolMode

logger = Logger("ps_test")

VDC_REL = 0.02
VDC_ZERO_ABS = 0.04
VDC_STEP_ABS = 0.05

VAC_REL = 0.03
VAC_STEP_ABS = 0.05
VAC_ZERO_ABS = 0.03

FREQ_REL = 0.01


def check(val: bool, message: str):
    if not val:
        logger.throw(message)


def wait_mode():
    time.sleep(1)


def _init_devices() -> Tuple[EdproPS, RigolDevice]:
    # init rigol
    rigol = RigolDevice()
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


def _dispose_devices(ps: Optional[EdproPS], ri: Optional[RigolDevice]):
    if ps: ps.close()
    if ri: ri.close()


def test_v_dc(ps: EdproPS, ri: RigolDevice) -> bool:
    rec = TestRecorder("test_vds")
    ri.mode(RigolMode.VDC_20)
    ps.cmd("mode dc")
    ps.cmd("set l 0")
    wait_mode()

    levels = [l for l in range(0, 50, 2)] + [0, 50, 0]

    for level in levels:
        step_u = 0.1 * level
        ps.cmd(f"set l {level}")
        ps_val = ps.request_values().U
        ri_val = ri.measure_vdc()
        ea = eabs(ps_val, ri_val)
        er = erel(ps_val, ri_val)
        rec.trace(f"step: {step_u:0.1f}V | ps: {ps_val:0.6f} | ri: {ps_val:0.6f} | abs: {ea:0.6f} | rel: {er * 100:0.2f}%")
        if level == 0:
            rec.expect_abs(ps_val, ri_val, VDC_ZERO_ABS)
        else:
            rec.expect_abs(step_u, ps_val, VDC_STEP_ABS)
            rec.expect_rel(ps_val, ri_val, 2 * VDC_REL)

    rec.print_result()
    return rec.success


def test_v_ac(ps: EdproPS, ri: RigolDevice) -> bool:
    rec = TestRecorder("test_vac")
    ri.mode(RigolMode.VAC_20)
    ps.cmd("mode ac")
    ps.cmd("set l 0")
    ps.cmd("set f 1000")
    wait_mode()

    levels = [l for l in range(0, 30, 2)] + [0, 30, 0]

    for level in levels:
        step_u = 0.1 * level
        ps.cmd(f"set l {level}")
        time.sleep(0.25)
        ps_val = ps.request_values().U
        ri_val = ri.measure_vac()
        ea = eabs(ps_val, ri_val)
        er = erel(ps_val, ri_val)
        rec.trace(f"step: {step_u:0.1f}V | ps: {ps_val:0.6f} | rigol: {ri_val:0.6f} | abs: {ea:0.6f} | rel: {er * 100:0.2f}%")
        if level == 0:
            rec.expect_abs(ps_val, ri_val, VAC_ZERO_ABS)
        else:
            rec.expect_abs(step_u, ps_val, VAC_STEP_ABS)
            rec.expect_rel(ps_val, ri_val, VAC_REL)

    rec.print_result()
    return rec.success


def test_freq(ps: EdproPS, ri: RigolDevice) -> bool:
    level = 30
    rec = TestRecorder("test_fr")
    ri.mode(RigolMode.FREQ_20)
    ps.cmd("mode ac")
    ps.cmd(f"set l {level}")
    wait_mode()

    def max_rel_u(frequency: float):
        if frequency < 50:
            return 0.3
        elif frequency < 100:
            return 0.05
        elif frequency < 10_000:
            return 0.02
        elif frequency < 100_000:
            return 0.03
        else:
            return 5.0

    fr = 10
    while fr <= 1_000_000:
        ps.cmd(f"set f {fr}")
        time.sleep(0.2)
        actual_u = ps.request_values().U
        actual_fr = ri.measure_freq()
        ea = eabs(fr, actual_fr)
        er = erel(fr, actual_fr)
        rec.trace(f"U: {actual_u: 0.3f}V | f: {fr} | actual: {actual_fr:0f} | abs: {ea:0f} | rel: {er * 100:0.2f}%")
        rec.expect_rel(fr, actual_fr, FREQ_REL)
        rec.expect_rel(0.1 * level, actual_u, max_rel_u(fr))
        if fr < 100:
            fr += 10
        elif fr < 1_000:
            fr += 100
        elif fr < 10_000:
            fr += 1_000
        elif fr < 100_000:
            fr += 10_000
        else:
            fr += 100_000

    ps.cmd("set l 0")
    ps.cmd("set f 1000")
    rec.print_result()
    return rec.success


def test_a_dc(ps: EdproPS, ri: RigolDevice) -> bool:
    rec = TestRecorder("tast_adc")
    ri.mode(RigolMode.VDC_20)
    ps.cmd("mode dc")
    ps.cmd("set l 0")
    wait_mode()

    rec.print_result()
    return rec.success


def ps_run_test():
    ps: Optional[EdproPS] = None
    ri: Optional[RigolDevice] = None
    try:
        ps, ri = _init_devices()

        choise = prompt("Connect Rigol to Powersource output. <Enter> - continue, <s> - skip: ")
        if choise == "":
            while True:
                try:
                    check(test_v_dc(ps, ri), "Test failed!")
                    check(test_v_ac(ps, ri), "Test failed!")
                    check(test_freq(ps, ri), "Test failed!")
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
    ri: Optional[RigolDevice] = None
    try:
        ps, ri = _init_devices()
        check(test_v_dc(ps, ri), "Test Failed!")
        check(test_v_ac(ps, ri), "Test Failed!")
        check(test_freq(ps, ri), "Test Failed!")
        # test_a_dc(ps, ri)

    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        _dispose_devices(ps, ri)


if __name__ == "__main__":
    _run()
