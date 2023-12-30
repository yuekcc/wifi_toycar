-- LuaTools需要PROJECT和VERSION这两个信息
PROJECT = "toycarctl"
VERSION = "1.0.0"

-- 引入必要的库文件(lua编写), 内部库不需要require
sys = require("sys")
require("sysplus")

DirectionMotor = {}
function DirectionMotor.new(a, b)
    return {
        channal_a = gpio.setup(a, 0, gpio.PULLUP),
        channal_b = gpio.setup(b, 0, gpio.PULLUP),
    }
end

function DirectionMotor.stop(self)
    self.channal_a(0)
    self.channal_b(0)
end

function DirectionMotor.left(self)
    self.channal_a(0)
    self.channal_b(1)
end

function DirectionMotor.right(self)
    self.channal_a(1)
    self.channal_b(0)
end

MainMotor = {}
function MainMotor.new(a, b, c, d)
    return {
        channal_a = gpio.setup(a, 0, gpio.PULLUP),
        channal_b = gpio.setup(b, 0, gpio.PULLUP),
        channal_c = gpio.setup(c, 0, gpio.PULLUP),
        channal_d = gpio.setup(d, 0, gpio.PULLUP),
    }
end

function MainMotor.left(self)
    self.channal_a(1)
    self.channal_b(0)
    self.channal_c(1)
    self.channal_d(0)
end

function MainMotor.right(self)
    self.channal_a(0)
    self.channal_b(1)
    self.channal_c(0)
    self.channal_d(1)
end

function MainMotor.stop(self)
    self.channal_a(0)
    self.channal_b(0)
    self.channal_c(0)
    self.channal_d(0)
end

local motors = {}
motors.direction = DirectionMotor.new(0, 1)
motors.main = MainMotor.new(4, 5, 12, 13)

function on_btn_press(btn)
    local log_tag = "on_btn_press";
    log.info(log_tag, "btn =>" .. btn)

    if btn == "left" then
        DirectionMotor.left(motors.direction)
    elseif btn == "right" then
        DirectionMotor.right(motors.direction)
    elseif btn == "front" then
        DirectionMotor.stop(motors.direction)
    elseif btn == "forward" then
        MainMotor.left(motors.main)
    elseif btn == "backward" then
        MainMotor.right(motors.main)
    elseif btn == "stop" then
        DirectionMotor.stop(motors.direction)
        MainMotor.stop(motors.main)
    else
        log.info(log_tag, "unknown button: " .. btn)
    end
end

function btn_contraller(uri)
    local log_tag = "btn_contraller"

    local btn = string.sub(uri, 14)
    log.info(log_tag, "btn =>" .. btn)
    if btn then
        on_btn_press(btn)
    end
end

function setup_station_mode()
    wlan.connect("sally", "@mo520$&")
    log.info("wlan", "wait for IP_READY")

    while not wlan.ready() do
        local ret, ip = sys.waitUntil("IP_READY", 30000)
        -- wlan连上之后, 这里会打印ip地址
        log.info("ip", ret, ip)
        if ip then
            _G.wlan_ip = ip
        end
    end
    log.info("wlan", "ready !!", wlan.getMac())
end

function setup_ap_mode()
    wlan.createAP("toycar", "123456789")
    log.info("wlan", "start in AP mode, password is 123456789")
    log.info("web", "pls open url http://192.168.4.1/")
end

function init_http_server()
    httpsrv.start(80, function(fd, method, uri, headers, body)
        local log_tag = "httpsrv"
        log.info(log_tag, method, uri)

        if string.find(uri, "/api/control/") == 1 then
            btn_contraller(uri)
            return 200, {}, "ok"
        end

        return 404, {}, "not found"
    end)
end

function init_system()
    log.info("init_system")
    -- 初始化 wlan
    sys.wait(1000)
    wlan.init()
    sys.wait(500)
    -- setup_station_mode()
    setup_ap_mode()
    sys.wait(500)

    init_http_server()
end

sys.taskInit(init_system)

sys.run()
