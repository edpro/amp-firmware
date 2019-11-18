# EdPro Amperia tools

### Download firmware and toolchain:

```bash
mkdir amperia
cd amperia
git clone https://github.com/edpro/firmware.git

# windows toolchain:
git clone https://github.com/edpro/toolchain.git
```


### OSX Toolchain:

On OSX only firmware flushing is supported (no calibration & tests)

* Install python3

* Install python libs: 

  `pip install esptool`

* Install UART driver: [Silicon Labs CP210x USB to UART Bridge](https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers)  


### Commands

```
./multimeter.sh
./powersource.sh
./accumulator.sh
```

