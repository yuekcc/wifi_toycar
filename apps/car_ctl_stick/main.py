from machine import Pin, I2C, ADC
import socket
import time

WLAN_SSID = ""
WLAN_PASSWORD = ""
API_SERVER_HOST = ""
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

def make_request(x_state):
    return "GET /api/control/{} HTTP/1.1\r\nHost: {}:{}\r\nUser-Agent: mpy-esp32\r\nAccept: application/json\r\n\r\n".format(x_state, API_SERVER_HOST, API_SERVER_PORT)


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
    
    last_x_state = ''
    while True:
        x_state = to_x_direct_enum(adc_x.read())
        print("x =", x_state)
        
        if x_state != last_x_state:
            body = make_request(x_state)
            print('send request', body)
            send_request(body.encode('utf8'))
            last_x_state = x_state
            
        #k_ = k.value()
        #print("x =", get_x())
        #print("y =", get_y())
        
        time.sleep(0.3)


main()
