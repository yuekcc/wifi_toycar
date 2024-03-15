from machine import Pin, ADC
import socket
import time
import network

WLAN_ESSID = "toycar"
WLAN_PASSWORD = "123456789"
API_SERVER_HOST = "192.168.4.1"
API_SERVER_PORT = 80

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

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


def get_y():
    return to_y_direct_enum(adc_y.read())


def make_request(x_state):
    url = f"/api/control/{x_state}"
    return f"GET {url} HTTP/1.1\r\nHost: {API_SERVER_HOST}:{API_SERVER_PORT}\r\nUser-Agent: mpy-esp32\r\nAccept: application/json\r\n\r\n"


def init_network():
    global API_SERVER_HOST

    if not wlan.isconnected():
        print(f"Try connect to '{WLAN_ESSID}' with password '{WLAN_PASSWORD}'")

        wlan.scan()
        wlan.connect(WLAN_ESSID, WLAN_PASSWORD)
        while not wlan.isconnected():
            pass
        ip, netmask, gateway, dns_addr = wlan.ifconfig()
        API_SERVER_HOST = gateway
    print(f"Connected to {WLAN_ESSID}, ip = {ip}")


def send_request(body):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((API_SERVER_HOST, API_SERVER_PORT))
        s.sendall(body.encode("utf8"))


def main():
    led1.off()
    led2.off()

    led1.on()
    init_network()
    led2.on()

    last_x_state = ""
    last_y_state = ""
    while True:
        if not wlan.isconnected():
            init_network()

        try:
            k_ = k.value()
            x_state = to_x_direct_enum(adc_x.read())
            y_state = to_y_direct_enum(adc_y.read())
            # print("x =", x_state, "y =", y_state, "k_ =", k_)

            if x_state != last_x_state:
                send_request(make_request(x_state))
                last_x_state = x_state

            if y_state != last_y_state:
                send_request(make_request(y_state))
                last_y_state = y_state

            if k_ == 0:
                send_request(make_request("stop"))
        except Exception:
            pass
        time.sleep(0.2)


main()
