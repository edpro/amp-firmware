PYTHON_PATH=$(realpath ../toolchain/python)
export PATH=$PYTHON_PATH:$PATH
echo "$(which python)"
echo "$(python --version)"
