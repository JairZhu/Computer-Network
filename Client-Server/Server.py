import struct
import socket
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('172.18.35.96', 8100))
server.listen(1)
print("Waiting for client's request...")

while True:
    connection, addr = server.accept()
    print("Connect IP:", addr[0], "Port:", addr[1])
    request = connection.recv(struct.calcsize('8s')).decode('utf-8')
    print("Receive", request, "request")
    if request == 'GET FILE':
        connection.send('test.mkv'.encode('utf-8'))
        connection.send(struct.pack('Q', os.stat('test.mkv').st_size))
        print("Sending", os.stat('test.mkv').st_size, "bytes test.mkv...")

        file = open('test.mkv', 'rb')
        sendsize = 0
        while True:
            data = file.read(2 ** 23)
            if not data:
                print('file send over')
                break

            sendsize += len(data)
            connection.send(data)
            print('Have sent', sendsize, "bytes")

    connection.close()