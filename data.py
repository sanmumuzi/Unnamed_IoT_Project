direction_map_tuple = (
    '左上方', '前上方', '右上方',
    '左前方', '正前方', '右前方',
    '左下方', '前下方', '右下方',
)

object_recognition_str_model = '{}在{}{}cm处。'
avoidance_str_model = '请注意：{}{}cm处有障碍物。'
general_object_recognition_str_model = '该方向有{}。'
limited_meter_object_recognition_str_model = '{}米之内有{}。'
obstacle_str_model = '障碍物是{}'

text_to_training_set = {  # map
    '飞机': 'aeroplane',
    '自行车': 'bicycle',
    '鸟': 'bird',
     '船': 'boat',
    '瓶子': 'bottle',
    '公共汽车': 'bus',
    '汽车': 'car',
    '猫': 'cat',
    '椅子': 'chair',
    '牛': 'cow',
    '餐桌': 'diningtable',
    '狗': 'dog',
    '马': 'horse',
    '摩托车': 'motorboke',
    '人': 'person',
    '盆栽': 'pottedplant',
    '羊': 'sheep',
    '沙发': 'sofa',
    '火车': 'train',
    '显示器': 'tvmonitor'
}

object_recognition_list = list(text_to_training_set.keys())

training_set_to_text = {
    'aeroplane': '飞机',
    'bicycle': '自行车',
    'bird': '鸟',
    'boat': '船',
    'bottle': '瓶子',
    'bus': '公共汽车',
    'car': '汽车',
    'cat': '猫',
    'chair': '椅子',
    'cow': '牛',
    'diningtable': '餐桌',
    'dog': '狗',
    'horse': '马',
    'motorbike': '摩托车',
    'person': '人',
    'pottedplant': '盆栽',
    'sheep': '羊',
    'sofa': '沙发',
    'train': '火车',
    'tvmonitor': '显示器'
}

network_classifications = ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car",
                           "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike",
                           "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

# with open('8092540_p0.jpg', 'rb') as f:
#     k = f.read()
#     print(k)

# x = subprocess.run(
#     'top -n 1',
#     shell=True,
#     stdout=subprocess.PIPE
# )


# proc = subprocess.Popen(
#     'ping www.baidu.com',
#     shell=True,
#     stdout=subprocess.PIPE
# )
#
# while proc.poll() is None:
#     output = proc.stdout.readline()
#     print(output)
