import struct
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('172.18.35.96', 8100))

client.send("GET FILE".encode('utf-8'))
print("Request a file")

while True:
    filename = client.recv(struct.calcsize('8s')).decode('utf-8')

    filesize, = struct.unpack('Q', client.recv(struct.calcsize('Q')))
    recievedsize = 0

    file = open(filename, 'wb')

    print('Start receiving', filesize, 'bytes', filename)

    while recievedsize != filesize:
        if filesize - recievedsize > 2 ** 23:
            data = client.recv(2 ** 23)
            recievedsize += len(data)
        else:
            data = client.recv(filesize - recievedsize)
            recievedsize = filesize

        file.write(data)
        print("Have received", recievedsize, "bytes")

    file.close()
    print('end receive...')
    client.close()
    break
