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
        dispatch_cmd('left')
        wait()
        dispatch_cmd('right')
        wait()
        dispatch_cmd('front')
        wait()
        dispatch_cmd('forward')
        wait()
        dispatch_cmd('backward')
        wait()
        dispatch_cmd('stop')
        wait()
