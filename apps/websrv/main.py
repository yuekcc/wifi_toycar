import network
import usocket as socket

response_headers = b'''
HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

'''

content = b'''
Hello world
'''

# setup wifi
ap = network.WLAN(network.AP_IF)
ap.config(essid='lalala', authmode=4, password='12345678')
ap.active(True)

def main():
    # 设置 socket 模式
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 端口用完后立即释放
    s.bind(socket.getaddrinfo('0.0.0.0', 80)[0][-1]) # 绑定端口
    s.listen(5) # 最大连接线 5
    
    print('lalala ready, hosted on', ap.ifconfig()[0])
    print('')
    
    while True:
        client_sock, client_addr = s.accept()
        print('client connected, addr =', client_addr)
        
        while True:
            h = client_sock.readline()
            print(h.decode('utf8'), end='')
            if h == b'' or h == b'\r\n':
                break
        
        client_sock.write(response_headers)
        client_sock.write(content)
        client_sock.close()

main()

