PYTHON_DIR=$(realpath ../toolchain/python)
export PATH=$PYTHON_DIR:$PYTHON_DIR/scripts:$PATH
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.
echo "$(which python)"
echo "$(python --version)"
