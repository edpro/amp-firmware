Binary images for all amperia devices

### Clone sources:

```
git clone https://github.com/edpro/firmware.git
```

### Windows Toolchain:

* Download `amperia_toolchain.zip` from the [Google Drive](https://drive.google.com/drive/folders/0B1MSlIDvzD9TV21lRmVJT1gxUlk?usp=sharing)
* Extract it alongside this repository directory

### OSX Toolchain:

* Install python3
* Install esptool: `pip install esptool`
* Install UART driver: [Silicon Labs CP210x USB to UART Bridge](https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers)  


### Commands

Flash first time:

```
./devicename-init.sh
```

Update firmware to a new version:

```
./devicename-update.sh
```

Connect to device log:

```
./log.sh
```





