import copy
import json
import math

import matplotlib.pyplot as plt
from setuptools import glob
from collections import deque

rs_map = {}
count = 0


def extract_data():
    files = deque(glob.glob("./data/*"))

    for file in files:
        data = json.load(open(file, mode='r'))
        x1 = data['eye_side'][0][0]
        y1 = data['eye_side'][0][1]
        x2 = data['eye_side'][1][0]
        y2 = data['eye_side'][1][1]
        face_w = math.dist((x1, y1), (x2, y2))
        t1 = 0.0 if x1 == x2 else math.degrees(math.atan((y2 - y1) / (x2 - x1)))
        print(t1)
        adjusted = adjust_data(data, x1, y1, t1, face_w)
        for k, v in adjusted.items():
            for i in range(len(v)):
                for j in range(len(v[i])):
                    key = f'{k}-{i}-{j}'
                    if key not in rs_map:
                        rs_map[key] = []
                    rs_map[key].append(v[i][j])
        print(adjusted)


def adjust_data(data, x1, y1, t1, face_w):
    adjusted = copy.deepcopy(data)
    for k, v in adjusted.items():

        for i in range(len(v)):
            x2 = v[i][0]
            y2 = v[i][1]
            t2 = 0.0 if x1 == x2 else math.degrees(math.atan((y2 - y1) / (x2 - x1)))
            dis = math.dist((x1, y1), (x2, y2))
            t3 = math.radians(t2 - t1)
            off_x = dis * math.cos(t3)
            off_y = dis * math.sin(t3)
            adjusted[k][i] = (-0.5 + (off_x / face_w), (off_y / face_w))

    return adjusted


if __name__ == '__main__':
    # print(get_degrees(0, 0, 1, -1))
    extract_data()
    # print(rs_map)
    # plt.hist(rs_map['l_eye_w-0-1'], bins=20)
    file = open(f'./handsome.json', mode='w')
    mode_map = {}
    for key, val in rs_map.items():
        n, bins, patches = plt.hist(val, bins=20)
        mode_index = n.argmax()
        mode_map[key] = (bins[mode_index] + bins[mode_index+1]) / 2

    json.dump(mode_map, file, indent=2, ensure_ascii=False)
    file.close()

    plt.show()
