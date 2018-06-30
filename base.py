from queue import Queue
import time
import subprocess
import json
import threading
from random import randint
import logging
from outdoor_navigation import direction
from collections import deque

FORMAT = '%(asctime)-15s %(user)-8s %(message)s'
logging.basicConfig(
    level=logging.DEBUG,
    # format=FORMAT,
)

logging.debug('开始导入各个自写模块')
try:
    from object_recognition import *
    from data import *
    from audio import *
    from nlp import nlp
except ImportError as e:
    logging.error('导入自写模块失败:{}'.format(e))
    raise

try:
    import thulac  # 预先加载
except ImportError as e:
    logging.error('无法导入语义分析模块...')
    raise
else:
    try:
        thu1 = thulac.thulac(user_dict='user_dict')
    except Exception:
        logging.error('初始化接口失败')
        raise

time.sleep(2)

text_to_audio = Queue()
say_str_queue = Queue()
# event = threading.Event()
# event.set()
camera_lock = threading.Lock()
audio_lock = threading.Lock()

'''
def construct_data(data):
    name_list = data[0]
    position_list = data[1]
    position_list = [item.replace('(', '').replace(')', '').split(',') for item in position_list]
    for i, j in enumerate(name_list):
        position_list[i].insert(0, j)
    return position_list
'''


def general_object_recognition():
    """
    通用物体识别
    :return: 被识别物体的名称的列表（在阈值之上）
    """
    name_list = []

    # completed = subprocess.run(
    #     'python3 object_recognition.py',  # Because shell parameter, we must use native str, not list.
    #     shell=True,
    #     stdout=subprocess.PIPE
    # )
    # struct_data_list = completed.stdout.decode('utf-8').split('\n')[:-1]

    logging.debug('通用物体识别组件开始运行')
    struct_data_list = achieve_general_object_recognition()
    logging.debug('通用物体识别组件结束运行')
    for data in struct_data_list:
        name_list.append(data[0])
    return name_list


def specific_object_recognition(object_name):
    temp_struct_data_list = []

    # completed = subprocess.run(
    #     'python3 object_recognition.py',  # Because shell parameter, we must use native str, not list.
    #     shell=True,
    #     stdout=subprocess.PIPE
    # )
    # struct_data_list = completed.stdout.decode('utf-8').split('\n')[:-1]

    logging.debug('特殊物体识别组件开始运行')
    struct_data_list = achieve_specific_object_recognition(object_name)
    logging.debug('特殊物体识别组件结束运行')
    map_name = text_to_training_set.get(object_name)
    for data in struct_data_list:
        name, x0, y0, x1, y1 = data
        if name == map_name:
            temp_struct_data_list.append(str(data))  # 将数字转为 str
    return temp_struct_data_list


def part_measuring_distance(struct_data_str):  # avoidance
    logging.debug('物体识别时的测距参数：{}'.format(struct_data_str))
    completed = subprocess.run(
        './realsense/v2.0/Local/bulid/Local {}'.format(struct_data_str),
        shell=True,
        stdout=subprocess.PIPE,
    )
    avoidance_data = completed.stdout.decode('utf-8')
    direction, distance = avoidance_data.strip().split()
    direction, distance = int(direction), int(float(distance))
    return direction, distance


# 这个函数可能会放到其他线程里去，可以要放入队列中
def speak_func():
    while True:
        speak_str = text_to_audio.get()
        logging.info('将由音频设备输出的音频为: {}'.format(speak_str))
        # 如果真的有人说一串代码进来注入攻击，那我觉得是真的扯淡了
        # java -cp.:/home/admin/Desktop/3s_project/Lxy/lib/* toVoice
        completed = subprocess.run(
            'java -cp .:/home/admin/3s_root/3s_project/Lxy/lib/* toVoice "{}" output.mp3'.format(speak_str),
            shell=True
        )
        logging.debug('音频播放结束...')


def convert_audio_to_text():
    while True:
        audio_file = audio_to_text.get()
        logging.info('------------------------------------将音频文件转换为文字-----------------------------------------')
        java_str = 'java -cp .:/home/admin/3s_root/3s_project/Lxy/lib/* toText {}'.format(audio_file)
        logging.info('--------------{}----------------'.format(java_str))
        completed = subprocess.run(
            'java -cp .:/home/admin/3s_root/3s_project/Lxy/lib/* toText {}'.format(audio_file),
            shell=True,
        )
        logging.debug('音频文件转化成功')
        audio_text_json_path = 'result.txt'
        # logging.debug('--------------------------people_say_json_str: {}--------------------------'.format(people_say_json_str))
        try:
            with open(audio_text_json_path, 'rt', encoding='utf-8') as f:
                say_str_data = json.load(f)
            say_str = say_str_data['result'][0]
        except Exception:
            continue
        else:
            say_str_queue.put(say_str)


def start_convert_audio():
    x = threading.Thread(target=convert_audio_to_text)
    x.setDaemon(True)
    x.start()


# def start_object_recognition(text_keyword=None):
#     if text_keyword is not None:
#         logging.debug('开启特殊物体识别系统')
#         logging.debug('特殊物体识别系统--物体识别部分开始运行')
#         struct_data_list = specific_object_recognition(text_keyword)
#         struct_data_str = [' '.join(struct_data_list)]
#
#         logging.debug('struct_data_str: {}'.format(struct_data_str))
#
#         logging.debug('特殊物体识别系统--物体识别部分结束运行')
#         logging.debug('特殊物体识别系统--物体测距开始运行')
#         avoidance_str = part_measuring_distance(struct_data_str)
#         logging.debug('特殊物体识别系统--物体测距结束运行')
#         speak_str = convert_avoidance_str(avoidance_str, recognition=True)
#     else:
#         logging.debug('开启通用物体识别系统')
#         name_list = general_object_recognition()
#         name_str = '、'.join(name_list)
#
#         logging.debug('name_str: {}'.format(name_str))
#
#         speak_str = general_object_recognition_str_model.format(name_str)
#     logging.debug('物体识别系统结束')
#     text_to_audio.put(speak_str)

def get_picture_data():
    subprocess.run(
        './TinyYolo/data/images/Photo',
        shell=True
    )


def start_object_recognition(text_keyword=None):
    with camera_lock:
        logging.debug('物体识别--获取图像')
        picture_data = get_picture_data()
        logging.debug('物体识别--获取图像结束')
    recognition_data = object_recognition(picture_data=picture_data)
    recognition_data = construct_data(recognition_data)
    logging.debug('recognition_data: {}'.format(recognition_data))
    if text_keyword:  # 特定物体识别
        logging.debug('物体识别--特殊物体识别')
        map_name = text_to_training_set.get(text_keyword)
        logging.debug('----------------------{}------------------------'.format(map_name))
        # 之前只实现单个物体的对应逻辑代码
        # recognition_data = [str(y) for x in recognition_data if x[0] == map_name for y in x[1:]]
        # recognition_data = ' '.join(recognition_data)
        temp_data_list = [[str(_) for _ in item[1:]] for item in recognition_data if item[0] == map_name]
        # example: [['0', '0', '1', '1'], ['4', '4', '5', '5']]
        recognition_data_list = [' '.join(item) for item in temp_data_list]
        # example: ['0 0 1 1', '4 4 5 5']
        logging.debug('物体识别--特殊物体识别结束')
        logging.debug('-----------------rocognition_data: {}----------------------'.format(recognition_data))

        if recognition_data_list:
            info_list = []
            for item in recognition_data_list:
                with camera_lock:
                    logging.debug('物体识别--物体测距')
                    direction, distance = part_measuring_distance(item)
                    logging.debug('物体识别--物体测距结束')
                info_list.append((text_keyword, direction, distance))
            speak_str = convert_part_object_recognition_str(info_list=info_list)
        else:
            speak_str = ''
    else:  # 通用物体识别
        logging.debug('物体识别--通用物体识别')
        recognition_data = [training_set_to_text.get(x[0]) for x in recognition_data]
        recognition_data = {item for item in recognition_data if item is not None}  # Use set, not a list, avoid duplicates.
        recognition_data = '、'.join(recognition_data)
        logging.debug('物体识别--通用物体识别结束')
        if recognition_data:
            speak_str = general_object_recognition_str_model.format(recognition_data)
        else:
            speak_str = ''

    logging.debug('speak_str = {}'.format(speak_str))
    logging.debug('物体识别系统结束')
    if speak_str:
        text_to_audio.put(speak_str)
    else:
        text_to_audio.put('前方没有被识别的物体')


def convert_part_object_recognition_str(info_list):
    # object recognition to audio_str
    speak_str = ''
    for name, direction, distance in info_list:  # 处理多个被识别的物体的方法
        try:
            logging.debug('---------------direction: {}---------------------'.format(direction))
            direction_zh = direction_map_tuple[direction-1]
        except IndexError:
            logging.error('------------------将方向代号转换为中文时出错--------------------')
        else:
            speak_str += object_recognition_str_model.format(name, direction_zh, distance)
    return speak_str


def start_general_recognition():
    start_object_recognition()  # Call without parameter.


def measuring_distance():  # general recognition
    completed = subprocess.run(
        # './realsense/Global/bulid/Global',  # 执行命令
        './realsense/v2.0/Global/bulid/Global',
        shell=True,
        stdout=subprocess.PIPE,
    )
    logging.debug('全局测距组件开始运行')
    avoidance_str = completed.stdout.decode('utf-8')
    logging.debug('------------------------------ pure global measure data: {}------------------------------------'.format(avoidance_str))
    logging.debug('全局测距组件结束运行')
    return avoidance_str


def convert_avoidance_str(direction, distance, recognition=False, name=None):
    # 不再支持图像识别输出字符串, 由另一函数代替
    # object recognition to audio_str or avoidance_audio_str
    try:
        direction_zh = direction_map_tuple[direction-1]
    except IndexError:
        return '测距识别出错'
    if recognition:
        return object_recognition_str_model.format(name, direction_zh, distance)  # object recognition
    else:
        return avoidance_str_model.format(direction_zh, distance)  # avoidance


def start_avoidance(text_to_audio):
    logging.debug('开启避障系统')
    before_direction = -1
    before_distance = 99999  # 这样做其实不好，重开线程之后会被重置
    avoidance_deque = deque(maxlen=2)  # 避免方向跳变引起的误报
    while True:
        with camera_lock:  # use camera_lock
            start = time.time()
            logging.debug('camera_lock acquire...')
            avoidance_str = measuring_distance()
            end = time.time()
            logging.debug('camera_lock release...')
            logging.debug('避障组件执行时间:{}'.format(end - start))
        logging.debug('avoidance_str = {}'.format(avoidance_str))
        try:
            direction, distance, obstacle_x, obstacle_y = avoidance_str.strip().split()  # 分析返回值
            direction, distance, obstacle_x, obstacle_y = int(direction), int(float(distance)), int(obstacle_x), int(obstacle_y)

            avoidance_deque.append(direction)

            # 方向不变， 距离前后差小于30cm.
            logging.debug('进行避障属性检测')
            if (direction == before_direction and ((before_distance - distance) <= 30)) or distance > 190:
                logging.debug('障碍信息被忽略...')
            else:
                sign = True
                for item in avoidance_deque:  # 有一次比较的是自己,不改了
                    if direction != item:
                        sign = False
                        break
                if sign:
                    logging.debug('障碍信息更新...')
                    before_direction = direction  # Update data
                    before_distance = distance
                    text_to_audio.put(convert_avoidance_str(direction, distance))
            time.sleep(1)  # 1s 延迟
        except ValueError:
            logging.error('--------------------避障出错了----------------------')
            pass


def start_avoidance_thread():
    avoidance_thread = threading.Thread(target=start_avoidance, args=(text_to_audio,))
    avoidance_thread.setDaemon(True)
    avoidance_thread.start()
    return avoidance_thread


def start_speak_thread():
    speak_thread = threading.Thread(target=speak_func)
    speak_thread.setDaemon(True)
    speak_thread.start()
    return speak_thread

def start_record_thread():
    x = threading.Thread(target=record_generator, args=('test_audio.wav',))
    x.setDaemon(True)
    x.start()


def start_button_thread():
    x = threading.Thread(target=button)
    x.setDaemon(True)
    x.start()


def start_indoor_navigation(*args):
    logging.debug('开启室内导航系统')


def start_outdoor_navigation(destination):
    logging.debug('开启室外导航系统')
    speak_str = direction(destination)
    if speak_str is not None:
        logging.debug('室外导航开始播报: {}'.format(speak_str))
        text_to_audio.put(speak_str)
    else:
        logging.debug('室外导航处理失败...')


func_list = [
    start_object_recognition,
    start_general_recognition,
    start_indoor_navigation,
    start_outdoor_navigation,
]


def text_parser(temp_text):
    # temp_list = [
    #     '杯子在哪里',
    #     '前方有什么东西',
    #     '我想去卧室',
    #     '带我去最近的超市',
    # ]
    # for x in temp_list:
    #     text_list = nlp(thu1, x)
    pass


# def test_data():
#     logging.debug('使用测试数据')
#     time.sleep(10)
#     say_str_queue.put('前方有什么东西')
#     time.sleep(10)
#     say_str_queue.put('人在哪里')
#     time.sleep(10)
#     say_str_queue.put('4米内有什么')
#     time.sleep(10)
#     say_str_queue.put('障碍物是什么')
#     time.sleep(10)
#     say_str_queue.put('带我去仙林南京大学')


# def use_test_data_thread():
#     thread = threading.Thread(target=test_data)
#     thread.setDaemon(True)
#     thread.start()


def start_limited_meter_object_recognition(meter_num):
    try:
        meter_num = int(meter_num)
    except Exception:
        meter_num = 3
    with camera_lock:
        logging.debug('物体识别--获取图像')
        picture_data = get_picture_data()
        logging.debug('物体识别--获取图像结束')
    recognition_data = object_recognition(picture_data=picture_data)
    recognition_data = construct_data(recognition_data)
    logging.debug('recognition_data: {}'.format(recognition_data))
    temp_data_list = [[str(_) for _ in item] for item in recognition_data]
    recognition_data_list = [(item[0], ' '.join(item[1:])) for item in temp_data_list]
    # example: [('person', '0 0 1 1'), ('car', '2 2 3 3'), ('person', '4 4 5 5')]
    if recognition_data_list:
        info_list = []
        for item_name, item_arg in recognition_data_list:
            with camera_lock:
                logging.debug('物体识别--物体测距')
                direction, distance = part_measuring_distance(item_arg)
                logging.debug('物体识别--物体测距结束')
            info_list.append((item_name, direction, distance))
        logging.debug('-------------info_list  {}---------------------'.format(info_list))
        text_list = [training_set_to_text.get(item[0]) for item in info_list if item[2] <= meter_num * 100]
        text_list = {item for item in text_list if item is not None}
        logging.debug('-------------------limit --------{}-----------------------'.format(text_list))
        text = '、'.join(text_list)
        if text:
            # speak_str = limited_meter_object_recognition_str_model.format(1, '椅子')
            speak_str = limited_meter_object_recognition_str_model.format(meter_num, text)
            text_to_audio.put(speak_str)
        else:
            text_to_audio.put('{}米之内没有被识别的物体'.format(meter_num))
    else:  # 这边写错了...以后改
        text_to_audio.put('{}米之内没有被识别的物体'.format(meter_num))
    # time.sleep(1)
    # speak_str = limited_meter_object_recognition_str_model.format(1, '椅子')
    # text_to_audio.put(speak_str)


def start_obstacle_recognition():
    with camera_lock:
        start = time.time()
        logging.debug('camera_lock acquire...')
        avoidance_str = measuring_distance()
        end = time.time()
        logging.debug('camera_lock release...')
        logging.debug('避障组件执行时间:{}'.format(end - start))
    logging.debug('avoidance_str = {}'.format(avoidance_str))
    direction, distance, obstacle_x, obstacle_y = avoidance_str.strip().split()  # 分析返回值
    direction, distance, obstacle_x, obstacle_y = int(direction), int(float(distance)), int(obstacle_x), int(obstacle_y)
    with camera_lock:
        logging.debug('物体识别--获取图像')
        picture_data = get_picture_data()
        logging.debug('物体识别--获取图像结束')
    recognition_data = object_recognition(picture_data=picture_data)
    recognition_data = construct_data(recognition_data)
    logging.debug('recognition_data: {}'.format(recognition_data))

    success_sign = False  # 这里并不考虑重框
    for item in recognition_data:
        logging.debug('------------------obstacle_x :{}--------------------obstacle_y :{}----------'.format(obstacle_x, obstacle_y))
        if (item[1] < obstacle_x < item[3]) and (item[2] < obstacle_y < item[4]):
            # success_sign = True
            text_to_audio.put(obstacle_str_model.format(training_set_to_text[item[0]]))
            break
    # ----------------
    # success_sign = True
    # text_to_audio.put('障碍物是椅子')
    # ---------------------------------------
    if not success_sign:
        text_to_audio.put('障碍物没有被识别')


def main_logic():
    temp_text = say_str_queue.get()
    global_fuck = 0  # 作假变量
    while temp_text is not None:
        func_num, *args = nlp(thu1, temp_text)
        # if global_fuck == 0:
        #     start_obstacle_recognition()  # 障碍物是什么
        #     global_fuck = 1
        # elif global_fuck == 1:
        #     start_general_recognition()  # 前方有什么
        #     global_fuck = 2
        # elif global_fuck == 2:
        #     start_object_recognition(*args)  # 人在那里
        #     global_fuck = 3
        # elif global_fuck == 3:
        #     start_limited_meter_object_recognition(*args)  # 1米内有什么
        #     global_fuck = 4
        # else:
        speak_str = direction('南邮广场')
        # if speak_str is not None:
        #     logging.debug('室外导航开始播报: {}'.format(speak_str))
        text_to_audio.put(speak_str)
        # if func_num == 0:
        #     start_object_recognition(*args)
        # elif func_num == 1:
        #     start_general_recognition()
        # elif func_num == 2:
        #     start_indoor_navigation(*args)
        # elif func_num == 3:
        #     start_outdoor_navigation(*args)
        # elif func_num == 4:  # 米数图像识别
        #     start_limited_meter_object_recognition(*args)
        # elif func_num == 5:  # 障碍物识别
        #     start_obstacle_recognition()

        temp_text = say_str_queue.get()


if __name__ == '__main__':
    # use_test_data_thread()
    # avoidance_thread = start_avoidance_thread()
    speak_thread = start_speak_thread()
    button_thread = start_button_thread()
    record_thread = start_record_thread()
    start_convert_audio()
    # use_test_data_thread()
    main_logic()
