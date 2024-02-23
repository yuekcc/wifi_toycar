from machine import Pin, I2C, ADC
import time

WLAN_SSID = ""
WLAN_PASSWORD = ""

led1 = Pin(12, Pin.OUT)
led2 = Pin(13, Pin.OUT)
k = Pin(5, Pin.IN)
x = Pin(0)
y = Pin(1)
adc_x = ADC(x, atten=ADC.ATTN_11DB)
adc_y = ADC(y, atten=ADC.ATTN_11DB)


def to_x_direct_enum(num):
    if num > 3000:
        return "left"
    elif num < 1500:
        return "right"
    else:
        return "middle"


def to_y_direct_enum(num):
    if num > 3000:
        return "down"
    elif num < 1500:
        return "up"
    else:
        return "middle"


def get_x():
    return to_x_direct_enum(adc_x.read())


def get_y():
    return to_y_direct_enum(adc_y.read())


def init_network():
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.scan()
        wlan.connect(WLAN_SSID, WLAN_PASSWORD)
        while not wlan.isconnected():
            pass
        led2.on()
        print("connect to wlan, ip =", wlan.ifconfig()[0])


def main():
    led1.off()
    led2.off()

    led1.on()
    init_network()

    while True:
        k_ = k.value()
        print("x =", get_x())
        print("y =", get_y())
        time.sleep(0.1)


main()
