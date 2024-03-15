import network
import socket
from machine import Pin

WLAN_ESSID = "toycar"
WLAN_PASSWORD = "123456789"

class Motor:
    def __init__(self, p1, p2):
        self._p1 = Pin(p1, Pin.OUT, drive=Pin.DRIVE_3)
        self._p2 = Pin(p2, Pin.OUT, drive=Pin.DRIVE_3)

    def clockwise(self):
        self._p1.on()
        self._p2.off()

    def counterclockwise(self):
        self._p1.off()
        self._p2.on()

    def stop(self):
        self._p1.off()
        self._p2.off()


# 方向电机
direct_motor = Motor(0, 1)

# 动力电机
m1 = Motor(4, 5)
m2 = Motor(2, 3)


def dispatch_cmd(cmd):
    # print("dispatch_cmd", cmd)
    if cmd == "left":
        direct_motor.counterclockwise()
    elif cmd == "right":
        direct_motor.clockwise()
    elif cmd == "front":
        direct_motor.stop()
    elif cmd == "forward":
        m1.clockwise()
        m2.clockwise()
    elif cmd == "backward":
        m1.counterclockwise()
        m2.counterclockwise()
    elif cmd == "stop":
        direct_motor.stop()
        m1.stop()
        m2.stop()
    else:
        print("unknown command: ", cmd)


def test_dispatch_cmd():
    import time

    def wait():
        time.sleep(2)

    while True:
        dispatch_cmd("left")
        wait()
        dispatch_cmd("right")
        wait()
        dispatch_cmd("front")
        wait()
        dispatch_cmd("forward")
        wait()
        dispatch_cmd("backward")
        wait()
        dispatch_cmd("stop")
        wait()


notfound = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain; charset=UTF-8\r\nX-Server: mpy\r\nConnection: close\r\n\r\n"

index_html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Toy car controller</title>
    <style>
      html {
        box-sizing: border-box;
        font-size: 16px;
      }

      *,
      *:before,
      *:after {
        box-sizing: inherit;
      }

      body,
      h1,
      h2,
      h3,
      h4,
      h5,
      h6,
      p,
      ol,
      ul {
        margin: 0;
        padding: 0;
        font-weight: normal;
      }

      ol,
      ul {
        list-style: none;
      }

      img {
        max-width: 100%;
        height: auto;
      }

      body {
        display: flex;
        height: 100vh;
      }

      .box {
        border: 4px solid #ccc;
        border-radius: 8px;
        width: 5rem;
        margin: auto;
        text-align: center;
        line-height: 3;
        font-size: 18px;
        font-weight: 600;
      }
      .box:active {
        background-color: green;
        color: #fff;
      }
    </style>
  </head>
  <body>
    <script>
      const controls = [];
      setTimeout(async () => {
        for (;;) {
          const control = controls.shift();
          if (control) {
            await control();
          }

          await new Promise((resolve) => setTimeout(resolve, 100));
        }
      }, 100);

      function send(btnName) {
        console.log('#add', btnName);
        controls.push(() => {
          console.log('#send', btnName);
          return fetch(`/api/control/${btnName}`);
        });
      }

      function pressLeft() {
        send('front')
        send('left')
      }

      function pressRight() {
        send('front')
        send('right')
      }
    </script>
    <div style="margin: auto 0; display: flex; gap: 5px; justify-content: space-between; user-select: none; width: 100%; padding: 20px">
      <div style="flex: initial; display: flex; gap: 5px">
        <div class="box" onclick="pressLeft()">左</div>
        <div class="box" onclick="send('front')">上</div>
        <div class="box" onclick="pressRight()">右</div>
      </div>
      <div style="flex: initial; display: flex; flex-direction: column; gap: 5px">
        <div class="box" onclick="send('forward')">前</div>
        <div class="box" onclick="send('stop')">停</div>
        <div class="box" onclick="send('backward')">后</div>
      </div>
    </div>
  </body>
</html>
"""


def get_header(mime_type):
    return f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}; charset=UTF-8\r\nX-Server: mpy\r\nConnection: close"


def reply_with_cmd_type(cmd_type):
    header = get_header("application/json")
    body = "{" + f'"cmd_type": "{cmd_type}"' + "}"
    return header + "\r\n\r\n" + body


def reply_with_index_html():
    header = get_header("text/html")
    return header + "\r\n\r\n" + index_html


def parse_request(chunk):
    first_newline = chunk.find("\r\n")
    first_double_newline = chunk.find("\r\n\r\n")
    target_line = chunk[:first_newline]
    body = chunk[first_double_newline + 4 :]

    http_method, url, version = target_line.split()

    return (http_method, url, version, body)


def handle_car_control(url):
    cmd_type = url[len("/api/control/") :]
    dispatch_cmd(cmd_type)
    return cmd_type


def on_connection(request):
    http_method, url, version, req_body = parse_request(request)
    print(http_method, url, version, req_body)

    response_body = ""
    if url == "/":
        response_body = reply_with_index_html()
    elif url.startswith("/api/control/"):
        cmd_type = handle_car_control(url)
        response_body = reply_with_cmd_type(cmd_type)
    else:
        response_body = notfound

    return response_body


def init_network():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=WLAN_ESSID, authmode=4, password=WLAN_PASSWORD)
    ap.active(True)
    return ap.ifconfig()[0]  # ip


def main():
    gateway_ip = init_network()
    print(f"Wifi toycar ready, ip = {gateway_ip}")
    print(f"You can connect to '{WLAN_ESSID}' with password '{WLAN_PASSWORD}'")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((gateway_ip, 80))
    s.listen(5)
    print(f"\nApi server hosted on http://{gateway_ip}:80")

    while True:
        client_s, addr = s.accept()
        with client_s:
            print(f"connected by {addr}")
            data = client_s.recv(1024)
            response = on_connection(data.decode("utf8"))
            client_s.sendall(response.encode("utf8"))


main()
