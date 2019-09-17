import sys
import os

from glob import glob
from typing import List

from tools.common.logger import Logger

logger = Logger("system")


def delete_files(pdir, mask):
    for file in glob(os.path.join(pdir, mask)):
        os.remove(file)


def run_shell(args: List[str], cwd: str = None):
    logger.info(f"{' '.join(args)}")
    sys.stdout.flush()
    retcode = os.subprocess.call(args, cwd=cwd)
    if retcode != 0:
        logger.throw(f"Command execution failed, exit code: {retcode}")
