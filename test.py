# # v1.2
# # created
# #   by Roger
# # in 2017.1.3
#
# import sys
#
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWebEngineWidgets import *
# from PyQt5.QtWidgets import *
#
#
# class MainWindow(QMainWindow):
#     # noinspection PyUnresolvedReferences
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # 设置窗口标题
#         self.setWindowTitle('B15011025')
#         # 设置窗口图标
#         self.setWindowIcon(QIcon('icons/penguin.png'))
#         # 设置窗口大小900*600
#         self.resize(900, 600)
#         self.show()
#
#         # 设置浏览器
#         self.browser = QWebEngineView()
#         url = 'http://blog.csdn.net/roger_lzh'
#         # 指定打开界面的 URL
#         self.browser.setUrl(QUrl(url))
#         # 添加浏览器到窗口中
#         self.setCentralWidget(self.browser)
#
#         ###使用QToolBar创建导航栏，并使用QAction创建按钮
#         # 添加导航栏
#         navigation_bar = QToolBar('Navigation')
#         # 设定图标的大小
#         navigation_bar.setIconSize(QSize(16, 16))
#         # 添加导航栏到窗口中
#         self.addToolBar(navigation_bar)
#
#         # QAction类提供了抽象的用户界面action，这些action可以被放置在窗口部件中
#         # 添加前进、后退、停止加载和刷新的按钮
#         back_button = QAction(QIcon('icons/back.png'), 'Back', self)
#         next_button = QAction(QIcon('icons/next.png'), 'Forward', self)
#         stop_button = QAction(QIcon('icons/cross.png'), 'stop', self)
#         reload_button = QAction(QIcon('icons/renew.png'), 'reload', self)
#
#         back_button.triggered.connect(self.browser.back)
#         next_button.triggered.connect(self.browser.forward)
#         stop_button.triggered.connect(self.browser.stop)
#         reload_button.triggered.connect(self.browser.reload)
#
#         # 将按钮添加到导航栏上
#         navigation_bar.addAction(back_button)
#         navigation_bar.addAction(next_button)
#         navigation_bar.addAction(stop_button)
#         navigation_bar.addAction(reload_button)
#
#         # 添加URL地址栏
#         self.urlbar = QLineEdit()
#         # 让地址栏能响应回车按键信号
#         self.urlbar.returnPressed.connect(self.navigate_to_url)
#
#         navigation_bar.addSeparator()
#         navigation_bar.addWidget(self.urlbar)
#
#         # 让浏览器相应url地址的变化
#         self.browser.urlChanged.connect(self.renew_urlbar)
#
#     def navigate_to_url(self):
#         q = QUrl(self.urlbar.text())
#         if q.scheme() == '':
#             q.setScheme('http')
#         self.browser.setUrl(q)
#
#     def renew_urlbar(self, q):
#         # 将当前网页的链接更新到地址栏
#         self.urlbar.setText(q.toString())
#         self.urlbar.setCursorPosition(0)
#
#
# # 创建应用
# app = QApplication(sys.argv)
# # 创建主窗口
# window = MainWindow()
# # 显示窗口
# window.show()
# # 运行应用，并监听事件
# app.exec_()


# async def test():
#     print('test start')
#     await asyncio.sleep(5)
#     print('test end')
#
#
#
# event_loop = asyncio.get_event_loop()
# event_loop.run_until_complete(test())
# print('test good!')

# import datetime
#
# async def display_date(loop):
#     end_time = loop.time() + 5.0
#     while True:
#         print(datetime.datetime.now())
#         if (loop.time() + 1.0) >= end_time:
#             break
#         await asyncio.sleep(1)
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(display_date(loop))
# loop.close()
#


# import asyncio
# import time
# async def compute(x, y):
#     print("Compute %s + %s ..." % (x, y))
#     await asyncio.sleep(1.0)
#     return x + y
#
# async def print_sum(x, y):
#     result = await compute(x, y)
#     print("%s + %s = %s" % (x, y, result))
#
# loop = asyncio.get_event_loop()
# k = []
# for i in range(1000):
#     k.append(print_sum(1, 2))
# t1 = time.time()
# loop.run_until_complete(
#     asyncio.gather(*k)
# )
# print(time.time() - t1)
# loop.close()

# import asyncio
#
# async def print_message(message, wait):
#     await asyncio.sleep(wait)
#     print(message)
#
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(asyncio.gather(
#     print_message('hello world', 1),
#     print_message('world hello', 0.5)
# ))
#
#

# RECORD_SECONDS = 5
# WAVE_OUTPUT_FILENAME = "output.wav"

'''
def recording():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
'''

from queue import Queue
import threading
import time
import wave
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
queue_item = Queue()


def record_thread(filename, stream, p):
    print('recording')
    wavefile = wave.open(filename, 'wb')
    wavefile.setnchannels(CHANNELS)
    wavefile.setsampwidth(p.get_sample_size(FORMAT))
    wavefile.setframerate(RATE)
    while RECORDING == 1:
        wavefile.writeframes(stream.read(CHUNK))
    wavefile.close()
    print('recording end.')


def record_generator(filename):
    global RECORDING
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    while True:
        queue_item.get()
        RECORDING = 1
        t = threading.Thread(target=record_thread, args=(filename, stream, p))
        t.setDaemon(True)
        t.start()
        queue_item.get()
        RECORDING = 0


def button():
    time.sleep(2)
    queue_item.put(1)
    time.sleep(5)
    queue_item.put(1)
    


if __name__ == '__main__':
    # recording()

    x = threading.Thread(target=record_generator, args=('test.wav',))
    x.setDaemon(True)
    x.start()
    y = threading.Thread(target=button)
    y.setDaemon(True)
    y.start()
    time.sleep(8)
    pass
