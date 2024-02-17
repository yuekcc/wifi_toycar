from machine import Pin

class Motor:
    def __init__(self, p1, p2):
        self._p1 = Pin(p1, Pin.OUT)
        self._p2 = Pin(p2, Pin.OUT)
    
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
m2 = Motor(12, 13)

def dispatch_cmd(cmd):
    if cmd == b'left':
        direct_motor.clockwise()
    elif cmd == b'right':
        direct_motor.counterclockwise()
    elif cmd == b'front':
        direct_motor.stop()
    elif cmd == b'forward':
        m1.clockwise()
        m2.clockwise()
    elif cmd == b'backward':
        m1.clockwise()
        m2.clockwise()
    elif stop == b'stop':
        direct_motor.stop()
        m1.stop()
        m2.stop()
    else
        print('unknown command: ', cmd)
