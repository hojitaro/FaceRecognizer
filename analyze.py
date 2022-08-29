import copy
import json
import math

import matplotlib.pyplot as plt
from setuptools import glob
from collections import deque

edges_list = ['eye_side', 'mouth_side', 'nose_side']
rs_map = {}
count = 0


def extract_data():
    files = deque(glob.glob("./data/*"))

    for file in files:
        data = json.load(open(file, mode='r'))
        face_w = 0
        for k in edges_list:
            x1 = data[k][0][0]
            y1 = data[k][0][1]
            x2 = data[k][1][0]
            y2 = data[k][1][1]
            dis = math.dist((x1, y1), (x2, y2))
            face_w = max(face_w, dis)

        cloned = copy.deepcopy(data)
        for k, v in data.items():
            for i in range(len(v)):
                x1 = v[i][0]
                y1 = v[i][1]
                cloned[k].remove(v[i])
                calc_parts_dis(cloned, f'{k}{i}', x1, y1, face_w)

            cloned.pop(k)


def calc_parts_dis(data, name, x1, y1, face_w):
    global count
    for k, v in data.items():
        for j in range(len(v)):
            x2 = v[j][0]
            y2 = v[j][1]
            dis = math.dist((x1, y1), (x2, y2))
            lis_k = f'{name}-{k}{j}'
            if lis_k not in rs_map:
                rs_map[lis_k] = []
            rs_map[lis_k].append(dis / face_w)

            count += 1


if __name__ == '__main__':
    extract_data()
    print(count)

    file = open(f'./handsome.json', mode='w')
    mode_map = {}
    for key, val in rs_map.items():
        n, bins, patches = plt.hist(val, bins=20)
        mode_index = n.argmax()
        mode_map[key] = (bins[mode_index] + bins[mode_index+1]) / 2

    json.dump(mode_map, file, indent=2, ensure_ascii=False)
    file.close()
    plt.show()
"""
x = [100, 200, 300, 400, 500, 600]
y = [10, 20, 30, 50, 80, 130]

plt.hist(x)
plt.show()
"""
