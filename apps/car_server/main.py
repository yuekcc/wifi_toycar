import network
import asyncio
from machine import Pin


class Motor:
    def __init__(self, p1, p2):
        self._p1 = Pin(p1, Pin.OUT)
        self._p2 = Pin(p2, Pin.OUT)

    def clockwise(self):
        """
        顺针方向转
        """

        self._p1.on()
        self._p2.off()

    def counterclockwise(self):
        """
        逆时针方向转
        """

        self._p1.off()
        self._p2.on()

    def stop(self):
        """
        停车
        """

        self._p1.off()
        self._p2.off()


# 方向电机
direct_motor = Motor(0, 1)

# 动力电机
m1 = Motor(4, 5)
m2 = Motor(12, 13)


def dispatch_cmd(cmd):
    print("dispatch_cmd", cmd)
    if cmd == "left":
        direct_motor.clockwise()
    elif cmd == "right":
        direct_motor.counterclockwise()
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


def get_header(mime_type):
    return "HTTP/1.1 200 OK\r\nContent-Type: {}; charset=UTF-8\r\nX-Server: mpy\r\nConnection: close".format(
        mime_type
    )


index_html = (
    get_header("text/html")
    + "\r\n\r\n"
    + """<!DOCTYPE html>
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
)


# setup wifi
ap = network.WLAN(network.AP_IF)
ap.config(essid="toycar", authmode=4, password="123456789")
ap.active(True)


def parse_request(chunk):
    first_newline = chunk.find("\r\n")
    first_double_newline = chunk.find("\r\n\r\n")
    target_line = chunk[:first_newline]
    body = chunk[first_double_newline + 4 :]

    http_method, url, version = target_line.split()

    return (http_method, url, version, body)


async def handle_connection(reader, writer):
    req = await reader.read(512)
    http_method, url, version, req_body = parse_request(req.decode("utf8"))
    print(http_method, url, version, req_body)

    if url == "/":
        writer.write(index_html.encode("utf8"))
    else:
        writer.write(notfound.encode("utf8"))

    await writer.drain()

    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_connection, "0.0.0.0", 80)
    print("toycar ready, hosted on http://%s:%d" % (ap.ifconfig()[0], 80))
    await server.wait_closed()


asyncio.run(main())
