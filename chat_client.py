import easygui
import sys
import socket
from PyQt6 import uic, QtWidgets, QtCore
from typing import Union

form_class = uic.loadUiType("chat.ui")[0]
running: bool = True
typing_text: str = ''
texts: str = ''
count: int = 0
name: Union[None, str] = None
text_from_socket: bytes = b''
ip: Union[None, str] = None
address: Union[None, int] = None
while ip is None:
    ip = easygui.enterbox("请输入服务器的ip地址/网址(不包含端口号):")
while address is None:
    address = easygui.integerbox('请输入端口号(10000~65535):', lowerbound=10000, upperbound=65535)
while name is None:
    name = easygui.enterbox("请输入用户名:")
connection = socket.create_connection((ip, address))
connection.setblocking(False)


class ChatWindow(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):
        global connection, name
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.send)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.read_from_socket)
        self.textEdit_2.setReadOnly(True)
        self.text_len = 0
        self.temp_text_len = 0
        connection.send(name.encode('utf-8') + b"\r\n")

    def refill(self, text: str):
        global texts, count, chat_window
        # chat_window.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        # chat_window.show()
        # 出现频繁闪屏,弃用
        if count == 0:
            texts += text
            self.text_len += len(text)
            self.temp_text_len = len(text)
        else:
            texts += "\n" + text
            self.text_len = self.text_len + len(text) + 1
            self.temp_text_len = len(text) + 1
        if count < 9:
            count += 1
        self.textEdit_2.setPlainText(texts)
        self.textEdit_2.verticalScrollBar().setValue(self.textEdit_2.verticalScrollBar().maximum())

    def read_from_socket(self):
        global connection, text_from_socket, running, texts
        try:
            data = connection.recv(8192)
        except BlockingIOError:
            return
        if not data:
            running = False
        for char in data:
            char = bytes([char])
            if char == b'\n':
                self.refill(text_from_socket.strip().decode('utf-8'))
                text_from_socket = b''
            else:
                text_from_socket += char

    def send(self):
        global connection
        if self.textEdit.toPlainText() != '' and self.textEdit.toPlainText() != '\n' and \
                self.textEdit.toPlainText() is not None:
            if '\n' in self.textEdit.toPlainText():
                temp_text_list = self.textEdit.toPlainText().split('\n')
                temp_text = '\n       '.join(temp_text_list).strip()
            else:
                temp_text = self.textEdit.toPlainText().strip()
            self.refill("你：" + temp_text)
            connection.send(self.textEdit.toPlainText().strip().encode('utf-8') + b'\r\n')
            self.textEdit.setPlainText('')


window_transparency: Union[None, int] = None
while window_transparency is None:
    window_transparency = easygui.integerbox('请输入窗口透明度(0~100):', lowerbound=0, upperbound=100) / 100
app = QtWidgets.QApplication(sys.argv)
chat_window = ChatWindow(None)
chat_window.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
chat_window.setWindowOpacity(window_transparency)
chat_window.show()
chat_window.timer.start(100)
app.exec()
connection.send(b'/quit\r\n')
sys.exit()
