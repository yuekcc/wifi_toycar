from machine import Pin, ADC
import socket
import time
import network

WLAN_SSID = "toycar"
WLAN_PASSWORD = "123456789"
API_SERVER_HOST = "192.168.4.1"
API_SERVER_PORT = 80

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
        return "front"  # middle


def to_y_direct_enum(num):
    if num > 3000:
        return "backward"
    elif num < 1500:
        return "forward"
    else:
        return "middle"  # middle


def get_x():
    return to_x_direct_enum(adc_x.read())


def make_request(x_state):
    url = "/api/control/{}".format(x_state)
    return "GET {} HTTP/1.1\r\nHost: {}:{}\r\nUser-Agent: mpy-esp32\r\nAccept: application/json\r\n\r\n".format(
        url, API_SERVER_HOST, API_SERVER_PORT
    )


def get_y():
    return to_y_direct_enum(adc_y.read())


def init_network():
    global API_SERVER_HOST

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.scan()
        wlan.connect(WLAN_SSID, WLAN_PASSWORD)
        while not wlan.isconnected():
            pass
        led2.on()
        ip, netmask, gateway, dns_addr = wlan.ifconfig()
        print("connect to wlan, ip =", ip)
        API_SERVER_HOST = gateway


def send_request(body):
    s = socket.socket()
    s.connect((API_SERVER_HOST, API_SERVER_PORT))
    s.send(body)
    s.close()


def main():
    led1.off()
    led2.off()

    led1.on()
    init_network()

    last_x_state = ""
    last_y_state = ""
    while True:
        try:
            k_ = k.value()
            x_state = to_x_direct_enum(adc_x.read())
            y_state = to_y_direct_enum(adc_y.read())
            # print("x =", x_state, "y =", y_state, "k_ =", k_)

            if x_state != last_x_state:
                body = make_request(x_state)
                print("send request", body)
                send_request(body.encode("utf8"))
                last_x_state = x_state

            if y_state != last_y_state:
                body = make_request(y_state)
                print("send request", body)
                send_request(body.encode("utf8"))
                last_y_state = y_state

            if k_ == 0:
                body = make_request("stop")
                print("send request", body)
                send_request(body.encode("utf8"))
        except Exception as e:
            print("some error", e)
        time.sleep(0.2)


main()
