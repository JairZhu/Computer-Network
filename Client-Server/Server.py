import struct
import socket
import os
import time
from tqdm import tqdm

# 定义服务号
list_file = 0
transmission = 1
get = 2

# 定义版本号
version = 1

# 定义头文件长度
head_length = struct.calcsize('bbQ')

# 服务器端的文件列表
files = [b'test.jpg', b'test.mp4']


# 报文头生成函数
def makehead(version, service_number, length):
    return struct.pack('bbQ', version, service_number, length)


# 监听来自客户端的TCP连接
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('172.18.35.96', 8100))
server.listen(1)

while True:
    print("Waiting for connection...")
    # 接受客户端的连接
    connection, addr = server.accept()
    print("Connect IP:", addr[0], "Port:", addr[1])
    # 发送报文头和服务器的文件列表
    connection.send(makehead(version, list_file, struct.calcsize('bbQ8sQ8sQ')))
    for file in files:
        connection.send(struct.pack('8sQ', file, os.stat(file).st_size))
    # 接收来自客户端的报文头
    headinfo = connection.recv(head_length)
    # 解析报文头
    Version, request_number, length = struct.unpack('bbQ', headinfo)
    if request_number == get:
        # GET请求
        file_name = connection.recv(length - head_length).decode()
        file_length = os.stat(file_name).st_size
        print('Client request: Get', file_name)
        print('Start sending', file_length, 'bytes', file_name)
        time.sleep(1)
        # 发送回应的报文头
        connection.send(makehead(version, transmission, head_length + file_length))
        # 读取文件
        file_info = open(file_name, 'rb')
        # 设置上传进度条
        t = tqdm(total=file_length, unit='bytes')
        sent_size = 0
        # 传输数据
        while True:
            data = b''
            if file_length - sent_size > 2 ** 20:
                data = file_info.read(2 ** 20)
                sent_size += len(data)
                t.update(len(data))
                connection.send(data)
            elif file_length - sent_size > 1024:
                data = file_info.read(2 ** 17)
                sent_size += len(data)
                t.update(len(data))
                connection.send(data)
            else:
                data = file_info.read(1024)
                sent_size += len(data)
                t.update(len(data))
                connection.send(data)
            # 判断是否发送完
            if sent_size >= file_length:
                t.close()
                break
        # 关闭文件
        file_info.close()
        # 关闭连接
        connection.close()
        print(file_name, 'send over', '\nConnection close')
