# import time
# import argparse
#
# parser = argparse.ArgumentParser()
# parser.add_argument('-t', dest='speak_str', action='store')
# args = parser.parse_args()
#
# speak_str = args.speak_str
#
# # 这个函数可能会放到其他线程里去，可以要放入队列中
# print('现在音响正在发音...内容是：{}'.format(speak_str))
# time.sleep(2)

from queue import Queue
import threading
import time
import wave
import pyaudio
import serial
import logging


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
queue_item = Queue()
audio_to_text = Queue()
ser = serial.Serial("/dev/ttyACM0", 9600)


def record_thread(filename, stream, p):
    print('recording')
    wavefile = wave.open(filename, 'wb')
    wavefile.setnchannels(CHANNELS)
    wavefile.setsampwidth(p.get_sample_size(FORMAT))
    wavefile.setframerate(RATE)
    while RECORDING == 1:
        wavefile.writeframes(stream.read(CHUNK))
    wavefile.close()
    audio_to_text.put(filename)
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
        logging.debug('----------------------开始录音----------------------------')
        RECORDING = 1
        t = threading.Thread(target=record_thread, args=(filename, stream, p))
        t.setDaemon(True)
        t.start()
        queue_item.get()
        logging.debug('-----------------------录音结束----------------------------')
        RECORDING = 0


def button():
    pre_data = 0
    while True:
        data = ser.readline().decode('ascii')
        # logging.debug('-------------------------------serial: {}-------------------------'.format(data))
        try:
            data = int(str(data)[0])
        except ValueError:  # 有的时候会为空
            continue
        else:
            if data == 1 and pre_data == 0:  # 0 -> 1
                logging.info('-------------------------------------录音按钮被按下----------------------------------------------')
                queue_item.put(1)
                pre_data = 1
            elif data == 0 and pre_data == 1:  # 1 -> 0
                logging.info('-------------------------------------录音按钮被放开----------------------------------------------')
                queue_item.put(1)
                pre_data = 0



# if __name__ == '__main__':
    #
    # x = threading.Thread(target=record_generator, args=('test.wav',))
    # x.setDaemon(True)
    # x.start()
    # y = threading.Thread(target=button)
    # y.setDaemon(True)
    # y.start()
    # time.sleep(20)
    # pass
