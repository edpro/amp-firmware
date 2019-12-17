PYTHON_DIR=$(realpath ../amp-toolchain/python)
export PATH=$PYTHON_DIR:$PYTHON_DIR/scripts:$PATH
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.
which python
python --version
