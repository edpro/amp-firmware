import sys
from glob import glob
from os import path, os, subprocess
from typing import List

from tools.common.logger import Logger

logger = Logger("system")

def delete_files(pdir, mask):
    for file in glob(path.join(pdir, mask)):
        os.remove(file)


def run_shell(args: List[str], cwd: str = None):
    logger.info(f"{' '.join(args)}")
    sys.stdout.flush()
    retcode = subprocess.call(args, cwd=cwd)
    if retcode != 0:
        logger.throw(f"Command execution failed, exit code: {retcode}")

