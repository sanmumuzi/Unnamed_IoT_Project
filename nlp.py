from collections import defaultdict
import logging
from data import object_recognition_list
logging.basicConfig(level=logging.DEBUG)

test_list = [
    '杯子在哪里',
    '前方有什么东西',
    '我想去卧室',
    '带我去最近的超市',
]

indoor_navigation_list = ['卧室', ]
outdoor_navigation_list = ['超市', '羊山公园', '公园', '仙林南京大学']


def nlp(thu, pending_text):  # 这个接口可是真tm的丑
    text_list = separate_words(thu, pending_text)
    print(text_list)
    tag_dict = classified(text_list)
    func_num = get_func_num(tag_dict)
    print('func_num: ', func_num)
    if func_num is None:
        return None, None
    elif func_num == 1:  # 普遍物体识别
        return func_num, None
    elif func_num == 4:
        # 这里经过一系列的字符串得出米数
        meter = tag_dict['m'][0]
        return func_num, meter
    elif func_num == 5:  # 障碍物检测
        return func_num, None
    else:
        for n_word in tag_dict['n']:
            print(func_num, n_word)
            return func_num, n_word
    return text_list


def separate_words(thu, pending_text):
    text_list = thu.cut(pending_text, text=False)
    text_list = composite(text_list)
    print('text_list = ', text_list)
    return text_list


def composite(text_list):  # 将ns和n词性进行合并
    temp_text = ''
    for item in tuple(text_list):
        if item[1] == 'ns' or item[1] == 'n':
            temp_text += item[0]
            text_list.remove(item)
    text_list.append([temp_text, 'n'])
    return text_list


# 如果是从前往后挨个处理的话，很明显这里是绝对可以优化的
# 二叉树
def classified(text_list):
    tag_dict = defaultdict(lambda: ExtendList())
    for word, tag in text_list:
        # tag_dict.setdefault(tag, [])
        tag_dict[tag].append(word)
    return tag_dict


def get_func_num(tag_dict):
    logging.debug(tag_dict)
    tag_n_list = tag_dict['n']
    print('tag_n_list: {}'.format(tag_n_list))

    if tag_n_list.is_exist(['障碍物', '障碍']):
        logging.debug('--------------------障碍物识别-------------------------')
        return 5
    if tag_dict['v'].is_exist(['有', '存在']):
        logging.debug('这应该是个普遍物体识别或者是限定米数的物体识别')
        if tag_dict['f'].is_exist(['内']) or tag_dict['q'].is_exist(['米']):
            logging.debug('--------------------限定米数的物体识别---------------------')
            return 4
        else:
            logging.debug('---------------------普遍物体识别-----------------------')
            return 1
    elif tag_n_list:
        try:
            tag_n_list.remove('')
        except ValueError:
            pass
        if tag_n_list:
            if tag_n_list.is_exist(['哪']) or tag_dict['v'].is_exist(['在', '去']):
                logging.debug('这应该是个特定物体识别或者室内室外导航')
            if tag_n_list.is_exist(object_recognition_list):
                logging.debug('-------为物体识别----------')
                return 0
            elif tag_n_list.is_exist(indoor_navigation_list):
                logging.debug('--------为室内导航---------')
                return 2
            # elif tag_n_list.is_exist(outdoor_navigation_list):
            else:
                logging.debug('--------为室外导航----------')
                return 3
    return None


class ExtendList(list):
    def __init__(self, elements=()):  # 突然想起一个问题，貌似传入可变参数，会出现巨大的问题
        super(ExtendList, self).__init__(elements)

    def is_exist(self, sequence):
        for item in self:
            if item in sequence:
                return True
        return False


if __name__ == '__main__':
    import thulac
    thu1 = thulac.thulac()
    nlp(thu1, '障碍是什么')
