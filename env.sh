export PATH=$(realpath ../toolchain/python):$PATH
echo $(which python)
echo $(python --version)

./check-updates.sh