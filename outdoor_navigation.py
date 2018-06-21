import json
import logging

import requests
from GPS import getGPS
from compass import getCompass

logging.basicConfig(level=logging.DEBUG)

SECURE_KEY = 'b629b685e4e036f3147bdbff3edfdf9f'
test_location = (118.926667, 32.118889)

navigation_str_template_1 = '沿{road}向{orientation}步行{distance}米{action}'
navigation_str_template_2 = '向{orientation}步行{distance}米{action}'
navigation_str_template_3 = '步行{distance}米{action}'
navigation_str_template_4 = '沿{road}步行{distance}米{action}'

getcode_url = 'http://restapi.amap.com/v3/geocode/geo?address={}&output=JSON&key={}'
direction_url = 'http://restapi.amap.com/v3/direction/walking?origin={},{}&destination={}&key={}'

origin_direction_map = {
    '北': 0,
    '东北': 1,
    '东': 2,
    '东南': 3,
    '南': 4,
    '西南': 5,
    '西': 6,
    '西北': 7,
}

relative_direction = ('前', '右前方向', '右', '右后方向', '后', '左后方向', '左', '左前方向')

print('-------------------------------------')


def get_my_location():  # 获取使用者的经纬度
    return getGPS()
    # return test_location


def get_current_direction():  # 获取当前使用之者的面朝方向
    return getCompass()
    # return (lambda: 180)()  # test: 面朝南


def get_destination_location(text):
    r = requests.get(getcode_url.format(text, SECURE_KEY))
    data = json.loads(r.text)
    try:
        return data['geocodes'][0]['location']
    except IndexError as e:
        return None


def calculate_index(orientation, deviation_angle):  # 计算相对方向索引
    absolute_direction_code = origin_direction_map[orientation]
    relative_direction_code = int((deviation_angle + 22.5) % 360 // 45)
    # logging.debug('相对方向编号: {}'.format(relative_direction_code))
    # logging.debug('绝对方向编号: {}'.format(absolute_direction_code))
    return absolute_direction_code - relative_direction_code


def convert_direction(data_list):  # 转换方向表示 eg: 东 -> 前
    navigation_list = []
    for data in data_list:
        # logging.debug(data)
        road, orientation, distance, action = data['road'], data['orientation'], data['distance'], data['action']
        if not action:  # 有的路径, action 为 []
            action = ''  # 末尾不会设置None
        if not orientation:
            orientation = None
        if not road:
            road = None
        if orientation is not None:
            try:
                # logging.debug('绝对方向为: {}'.format(orientation))
                orientation = relative_direction[calculate_index(orientation, get_current_direction())]
                # logging.debug('相对方向为: {}'.format(orientation))
            except Exception:
                logging.debug('----------------绝对方向转换失败-------------------')
                raise
        if orientation is not None and road is not None:
            navigation_str = navigation_str_template_1.format(road=road, orientation=orientation, distance=distance,
                                                              action=action)
        elif orientation is not None:
            navigation_str = navigation_str_template_2.format(orientation=orientation, distance=distance, action=action)
        elif road is not None:
            navigation_str = navigation_str_template_4.format(road=road, distance=distance, action=action)
        else:
            navigation_str = navigation_str_template_3.format(distance=distance, action=action)
        navigation_list.append(navigation_str)
    logging.debug(navigation_list)
    return navigation_list


def direction(text):  # 命名不合适, 暂且不改
    speak_str = None
    my_location = get_my_location()
    print('my_location: {}'.format(my_location))
    if my_location is not None:
        destination_location = get_destination_location(text=text)
        print('destination_location: {}'.format(destination_location))
        if destination_location is not None:
            r = requests.get(direction_url.format(my_location[0], my_location[1], destination_location, SECURE_KEY))
            with open('path.json', 'wt', encoding='utf-8') as f:  # 没必要，暂时不改了
                f.write(r.text)
            data = json.loads(r.text)
            try:
                # speak_str = data['route']['paths'][0]['steps'][0]['instruction']
                data_list = data['route']['paths'][0]['steps']
                data_list = convert_direction(data_list)  # 统一转变方向, 返回speak_str
                speak_str = data_list[0]
            except (IndexError, KeyError):
                pass
    return speak_str


if __name__ == '__main__':
    # r = requests.get('http://restapi.amap.com/v3/geocode/regeo?output=JSON&location=118.926667,32.118889&key={}'.format(SECURE_KEY))
    print(direction('南京大学'))
