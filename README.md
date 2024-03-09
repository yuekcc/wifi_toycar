# Wifi 遥控车

使用 ESP32-C3 控制遥控车，ESP32-C3 + micropython。

| 模块                                     | 用途         | 价格    | 数量 |
| ---------------------------------------- | ------------ | ------- | ---- |
| [合宙 ESP32C3-CORE 开发板][ESP32C3-CORE] | 控制板       | ￥ 13.9 | 2    |
| [HS-F04A 电机驱动模块][HS-F04A]          | 方向电机控制 | ￥ 2.5  | 1    |
| [HS-F09C 双路电机驱动板][HS-F09C]        | 动力电机控制 | ￥ 3.5  | 1    |
| 18650 电池                               | 供电         | ￥ 8.75 | 3    |

[ESP32C3-CORE]: https://wiki.luatos.com/chips/esp32c3/board.html
[HS-F04A]: http://www.hellostem.cn/?chuanganqipeijiandeng/hs_f04adianjiqudongmokuai.html
[HS-F09C]: http://www.hellostem.cn/?chuanganqipeijiandeng/s_f09abshuangludianjiqudongban.html

## 开发工具

IDE 可以用 [thonny](https://github.com/thonny/thonny/releases/tag/v4.1.4)。thonny 集成了 esptool 和 micropython 插件。

> 当然也可以使用 vscode。vscode 可以使用 pycom 插件。通过 pycom 插件也可以直接上传文件到板子。打码不是 vscode 比较方便。

开发板刷 ROM 需要 [esptool](https://pypi.org/project/esptool/)。esptool 是基于 python 的 ESP 刷机工具，可以通过 pip 安装。thonny 已经内置 esptool，不需要额外安装。

## 烧录 MicroPython ROM

**以下命令是通过 thonny 的 Open system shell 打开的 shell 中执行**。通过 thonny 打开 shell，会设置相应的环境变量，可以使用 esptool。

> 入口 thonny -> Tools 菜单 -> Open system shell

参考：https://www.bilibili.com/read/cv15460009/

### 确认 COM 口

首先是确定连接板子的 COM 口。windows 11 一般情况下不需要安装驱动。如果找到没有识别的设备，可以试试安装相应的驱动。

> 如果还是没有找设备，可以检查 USB 线和电脑的 USB 插口。换不同的插口，可能有奇效。

通过下面的命令查找开发板使用的 COM 口

```sh
reg query "HKEY_LOCAL_MACHINE\HARDWARE\DEVICEMAP\SERIALCOMM"
```

我的机器上显示：

```sh
Z:\>reg query "HKEY_LOCAL_MACHINE\HARDWARE\DEVICEMAP\SERIALCOMM"

HKEY_LOCAL_MACHINE\HARDWARE\DEVICEMAP\SERIALCOMM
    \Device\USBSER000    REG_SZ    COM4


Z:\>
```

每个机器可能不同的。注意区分。

### 擦除自带的 ROM

执行命令：

```
esptool.py --chip esp32-c3 --port COM4 erase_flash
```

输出如下：

```sh
esptool.py v4.7.0
Serial port COM4
Connecting...
Chip is ESP32-C3 (QFN32) (revision v0.4)
Features: WiFi, BLE
Crystal is 40MHz
MAC: ec:da:3b:d1:4a:34
Uploading stub...
Running stub...
Stub running...
Erasing flash (this may take a while)...
Chip erase completed successfully in 2.9s
Hard resetting via RTS pin...
```

## 刷入 MicroPython ROM

MicroPython ROM 尽量使用新版本。

执行命令：

```
esptool.py --chip esp32-c3 --port COM4 --baud 460800 write_flash -z 0x0 ESP32_GENERIC_C3-20240105-v1.22.1.bin
```

输出如下：

```sh
Serial port COM4
Connecting...
Chip is ESP32-C3 (QFN32) (revision v0.4)
Features: WiFi, BLE
Crystal is 40MHz
MAC: ec:da:3b:d1:4a:34
Uploading stub...
Running stub...
Stub running...
Changing baud rate to 460800
Changed.
Configuring flash size...
Flash will be erased from 0x00000000 to 0x00196fff...
Compressed 1664080 bytes to 998285...
Wrote 1664080 bytes (998285 compressed) at 0x00000000 in 6.6 seconds (effective 2011.8 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```

`ESP32_GENERIC_C3-20240105-v1.22.1.bin` 文件可以在 [micropython.org](https://micropython.org/download/ESP32_GENERIC_C3/) 下载。注意需要选择 **ESP32-C3** 芯片的 bin 文件。

完成后按提示重启开发板。

## 测试

先在 thonny 中设置 Interpreter。在 thonny 右下角可以找到可用的 Python 解释器，选择 `MicroPython (ESP32) @ COM4`。然后新建一个文件，编写代码：

```py
from machine import Pin, I2C
import time

led1 = Pin(12, Pin.OUT)
led2 = Pin(13, Pin.OUT)

while True:
    led1.on()
    time.sleep(0.5)
    led1.off()
    led2.on()
    time.sleep(0.5)
    led2.off()
```

然后在 Run 菜单中找到 **Run current script**，就可以在开发板上执行上面的脚本。顺利的话，就可以看到板载的 LED 灯在闪烁。

## 上传代码

通过 thonny 可以很方便上传代码到板子上：

![保存到设备](assets/upload_to_device.png)

如果开发板在解释执行脚本，可能无法保存。可以先停止执行，再尝试保存到开发板。
