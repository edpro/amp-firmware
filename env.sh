PYTHON_PATH=$(realpath ../toolchain/python)
export PATH=$PYTHON_PATH:$PATH
export PYTHONDONTWRITEBYTECODE=1
echo "$(which python)"
echo "$(python --version)"
