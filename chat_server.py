import select
import socket
import easygui
from typing import Union
ip: Union[None, str] = None
address: Union[None, int] = None
while ip is None:
    ip = easygui.enterbox("请输入需要开启服务器的ip地址/网址(留空为localhost)\n(如无公网ip/公网网址,请直接使用localhost+内网穿透!):")
if ip == '':
    ip = 'localhost'
while address is None:
    address = easygui.integerbox('请输入端口号(10000~65535):', lowerbound=10000, upperbound=65535)
names: list = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((ip, address))
server_socket.listen()
server_socket.setblocking(False)
client_sockets: list = []
client_objects: dict = {}
all_texts: str = ''


class Client:
    def __init__(self, server_to_client_socket):
        self.socket = server_to_client_socket
        self.text_typed: bytes = b""
        self.username: Union[None, str] = None
        for client_object in client_objects.values():
            if client_object == self or client_object.username is None:
                continue
        server_to_client_socket.setblocking(False)

    def receive_data(self):
        data = self.socket.recv(8192)
        if not data:
            self.close_connection()
            return
        for char in data:
            char = bytes([char])
            if char == b'\n':
                self.handle_command(self.text_typed.strip())
                self.text_typed = b""
            else:
                self.text_typed += char

    def handle_command(self, command):
        global client_objects, all_texts, names
        if self.username is None:
            self.username = command
            for client_object in client_objects.values():
                if client_object == self or client_object.username is None:
                    continue
                client_object.socket.send(b'[' + self.username + b']' + '进入聊天室.'.encode('utf-8') + b'\r\n')
        elif command == b'/quit':
            self.close_connection()
            for client_object in client_objects.values():
                if client_object == self or client_object.username is None:
                    continue
                client_object.socket.send(b'[' + self.username + b']' + '离开聊天室.'.encode('utf-8') + b'\r\n')
        else:
            msg = b'[' + self.username + b']: ' + command + b'\r\n'
            for client_object in client_objects.values():
                if client_object == self or client_object.username is None:
                    continue
                client_object.socket.send(msg)
                all_texts += '\n' + msg.decode(encoding='utf-8')

    def close_connection(self):
        global client_sockets, client_objects
        client_sockets.remove(self.socket)
        del client_objects[self.socket.fileno()]
        self.socket.close()

    def kick(self):
        for client_object in client_objects.values():
            if client_object == self:
                client_object.socket.send('/kick-by-administrator\r\n')


while True:
    ready_to_read = select.select([server_socket] + client_sockets, [], [])[0]
    for sock in ready_to_read:
        if sock == server_socket:
            new_connection, address = sock.accept()
            client_sockets.append(new_connection)
            client_objects[new_connection.fileno()] = Client(new_connection)
            server_socket.listen()
        else:
            client_objects[sock.fileno()].receive_data()
