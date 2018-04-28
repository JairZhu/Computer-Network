import struct
import socket
from tqdm import tqdm
import time

# 定义服务号
list_file = 0
transmission = 1
get = 2
# 定义版本号
version = 1
user_choose = ''
# 定义头文件长度
head_length = struct.calcsize('bbQ')


# 报文头生成函数
def makehead(version, request_number, length):
    return struct.pack('bbQ', version, request_number, length)


# 与服务器建立连接
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('172.18.35.96', 8100))

while True:
    # 接受来自服务器的报文头
    headinfo = client.recv(head_length)
    # 解析报文头
    Version, service_number, packet_length = struct.unpack('bbQ', headinfo)
    # 解析服务号
    if service_number == list_file:
        # 获取列表信息服务
        receive_length = 0
        files_info = {}
        # 解析服务器发送过来的文件列表
        while receive_length != packet_length - head_length:
            receive_length += struct.calcsize('8sQ')
            file_name, file_length = struct.unpack('8sQ', client.recv(struct.calcsize('8sQ')))
            files_info[file_name.decode()] = file_length
        # 显示服务器上可下载的文件信息
        for key, value in files_info.items():
            print(key, '\t', value, 'bytes')
        # 获取用户输入
        user_choose = input('Please choose the file: ')
        # 解析用户输入
        while user_choose not in files_info.keys():
            user_choose = input(user_choose + 'does not exit, Please input again: ')
        else:
            # 生成请求报文并发送给服务器
            client.send(makehead(version, get, struct.calcsize('bbQ%ds' % len(user_choose))))
            client.send(user_choose.encode())

    elif service_number == transmission:
        # 数据传输服务
        recieved_length = 0
        file_length = packet_length - head_length
        file = open(user_choose, 'wb')
        print('Start receiving', file_length, 'bytes', user_choose)
        time.sleep(1)
        # 设置下载进度条
        t = tqdm(total=file_length, unit='bytes')
        # 下载服务器上的文件
        while recieved_length != file_length:
            if file_length - recieved_length > 2 ** 20:
                data = client.recv(2 ** 20)
                file.write(data)
                t.update(len(data))
                recieved_length += len(data)
            elif file_length - recieved_length > 1024:
                data = client.recv(2 ** 17)
                file.write(data)
                t.update(len(data))
                recieved_length += len(data)
            else:
                data = client.recv(1024)
                file.write(data)
                t.update(len(data))
                recieved_length = len(data)
            # 判断是否接收完
            if recieved_length >= file_length:
                break
        t.close()
        # 关闭文件
        file.close()
        print('Recieved', recieved_length, 'bytes', user_choose)
        # 关闭连接
        client.close()
        print('Connection close')
        break
    else:
        # 出现错误则关闭连接
        print('Error Occur!')
        client.close()
