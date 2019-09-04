from tools.common.logger import Logger, LoggedError
from tools.mm_context import MMContext

logger = Logger("mm_cal")


def mm_run_calibration():
    ctx = MMContext()
    try:
        ctx.init()
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        ctx.dispose()


def run_test():
    ctx = MMContext()
    try:
        ctx.init()
        logger.success()
    except LoggedError:
        pass
    except Exception:
        raise
    finally:
        ctx.dispose()


if __name__ == "__main__":
    run_test()
