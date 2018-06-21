# import time
#
#
# time.sleep(1)
# # print('recognize success.')
#
# print('cat', 0, 0, 1920, 1080)  # 30 is scale
# print('dog', 0, 0, 800, 600)
# print('student', 0, 0, 400, 200)
# print('cat', 0, 0, 500, 123)

import logging

from TinyYolo import caffe_objecet_direction


def achieve_general_object_recognition():
    print('内部实现')
    print('返回在一个阈值之上所有能识别的物体，阈值由你自己定')
    # return ['cat', 'dog', 'student']
    # 或者
    return [
        ('cat', 0, 0, 1920, 1080),  # 两种return选择一种就行
        ('dog', 0, 0, 800, 600),
        ('student', 0, 0, 400, 200)
    ]


def achieve_specific_object_recognition(object_name):
    print('内部实现')
    print('仅返回符合object_name的，如果识别不出和这个名称一样的物体，返回None')
    return [('cat', 0, 0, 1920, 1080)]  # 只返回最适合的一组


def object_recognition(picture_data):  # 极端值 会报错!!!!!!!!!!!!!!!!!!!!
    recognition_data_list = caffe_objecet_direction.caffe_objecet_direction.main()
    for i in range(len(recognition_data_list)):
        center_x = int(recognition_data_list[i][1] * 4.28)
        width = int(recognition_data_list[i][3] * 4.28)
        center_y = int(recognition_data_list[i][2] * 2.41)
        height = int(recognition_data_list[i][4] * 2.41)

        recognition_data_list[i][1] = int(center_x - width / 2)
        recognition_data_list[i][2] = int(center_y - height / 2)
        recognition_data_list[i][3] = int(center_x + width / 2)
        recognition_data_list[i][4] = int(center_y + height / 2)

        for j in range(1, 5):
            if recognition_data_list[i][j] < 0:
                recognition_data_list[i][j] = 0

    # recognition_data_list.append(['chair', 850, 720, 1280, 1080, 0.5])  # test数据
    return recognition_data_list


def test():
    temp = object_recognition(picture_data=get_picture_data())
    name_list = temp[0]
    position_list = temp[1]
    result = zip(temp[0], [x.replace('(', '').replace(')', '').split(',') for x in temp[1]])
    for x in result:
        print(x)


# def construct_data(data):
#     name_list = data[0]
#     position_list = data[1]
#     position_list = [item.replace('(', '').replace(')', '').split(',') for item in position_list]
#     for i, j in enumerate(name_list):
#         position_list[i].insert(0, j)
#     return position_list


def construct_data(data):
    logging.debug('--------------data : {}--------------'.format(data))
    return [item[:-1] for item in data if item[-1] > 0.15]


# recognition_data = construct_data(data=object_recognition(picture_data=get_picture_data()))
# map_name = 'person'
# print(recognition_data)
# recognition_data = [x for x in recognition_data if x[0] == map_name]
# print(recognition_data)
#
# recognition_data = [y for x in recognition_data if x[0] == map_name for y in x]
# recognition_data = ' '.join(recognition_data)
# print(recognition_data)

if __name__ == '__main__':
    rel = construct_data(object_recognition())
    print(rel)
