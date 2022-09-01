import copy
import json
import math

import matplotlib.pyplot as plt
from setuptools import glob


def extract_data():
    rs_lst = []
    for file in glob.glob('./data/handsome/*'):
        data = json.load(open(file, mode='r'))
        x = data['eye_side'][0][0]
        y = data['eye_side'][0][1]
        face_w, t = get_face_line(data)
        generic = get_generic_data(data, x, y, t, face_w)
        rs_lst.append(generic)

    return rs_lst, get_serial_map(rs_lst)


def get_generic_data(data, x1, y1, t1, face_w):
    generic = copy.deepcopy(data)
    for k, v in generic.items():
        for i in range(len(v)):
            x2 = v[i][0]
            y2 = v[i][1]
            dis = math.dist((x1, y1), (x2, y2))
            t2 = get_generic_deg(x1, y1, x2, y2)
            off_x = 0
            off_y = 0
            if (t2 and t1) is not None:
                t3 = math.radians(t2 - t1)
                off_x = dis * math.cos(t3)
                off_y = dis * math.sin(t3)
            generic[k][i] = (-0.5 + (off_x / face_w), (off_y / face_w))

    return generic


def get_serial_map(lst):
    ser_map = {}
    for data in lst:
        for k, v in data.items():
            for i in range(len(v)):
                for j in range(len(v[i])):
                    key = f'{k}-{i}-{j}'
                    if key not in ser_map:
                        ser_map[key] = []
                    ser_map[key].append(v[i][j])

    return ser_map


def analyze_hds():
    lst, ser_map = extract_data()
    st_map = {}
    for data in lst:
        for k, v in data.items():
            for i in range(len(v)):
                loc = []
                for j in range(len(v[i])):
                    key = f'{k}-{i}-{j}'
                    avr = sum(ser_map[key]) / len(ser_map[key])
                    loc.append(avr)
                st_map[f'{k}-{i}'] = loc

    file = open(f'./data/handsome.json', mode='w')
    json.dump(st_map, file, indent=2, ensure_ascii=False)
    file.close()


def get_generic_deg(x1, y1, x2, y2):
    dis = math.dist((x1, y1), (x2, y2))
    theta = None if dis == 0 else math.degrees(math.asin((y2 - y1) / dis))
    return theta if x1 <= x2 else 180.0 - theta if x1 > x2 else None


def get_face_line(data):
    x1 = data['eye_side'][0][0]
    y1 = data['eye_side'][0][1]
    x2 = data['eye_side'][1][0]
    y2 = data['eye_side'][1][1]
    face_w = math.dist((x1, y1), (x2, y2))
    theta = get_generic_deg(x1, y1, x2, y2)
    return face_w, theta


def analyze_otrs(target_path):
    sco_map = {}
    total_lst = []
    hds = json.load(open(f'./data/handsome.json', mode='r'))
    t_json = json.load(open(target_path, mode='r'))
    t_face_w, t_t = get_face_line(t_json)
    t_x = t_json['eye_side'][0][0]
    t_y = t_json['eye_side'][0][1]
    t_total = 0
    target = get_generic_data(t_json, t_x, t_y, t_t, t_face_w)

    for file in glob.glob('./data/others/*'):
        data = json.load(open(file, mode='r'))
        x = data['eye_side'][0][0]
        y = data['eye_side'][0][1]
        face_w, t = get_face_line(data)
        generic = get_generic_data(data, x, y, t, face_w)
        total = 0
        for k, v in generic.items():
            for i in range(len(v)):
                key = f'{k}-{i}'
                if key not in sco_map:
                    sco_map[key] = []

                dis = math.dist(v[i], hds[key])
                score = (0.1 - dis) * 1000
                sco_map[key].append(score)
                total += score

        total_lst.append(total)

    for k, v in target.items():
        for i in range(len(v)):
            key = f'{k}-{i}'
            dis = math.dist(v[i], hds[key])
            score = (0.1 - dis) * 1000
            avr, s_dev, dev = calc_dev(sco_map[key], score)
            t_total += score

            for v2 in sco_map[key]:
                s_dev += (v2 - avr) ** 2
            s_dev = math.sqrt(s_dev / len(sco_map[key]))
            if s_dev != 0:
                dev = (score - avr) / s_dev * 10 + 50

            sco_lst = sorted(sco_map[key], reverse=True)
            rank = calc_rank(sco_lst, score)
            print(f'part={key} score={score}, deviation value={dev}, rank={rank},'
                  f' standard deviation={s_dev}, average={avr}')

    total_lst = sorted(total_lst, reverse=True)
    t_rank = calc_rank(total_lst, t_total)
    avr, s_dev, dev = calc_dev(total_lst, t_total)
    print(f'total score={t_total}, deviation value={dev}, rank={t_rank}, standard deviation={s_dev}, average={avr}')

    #plt.hist(sco_map['mouth_side-0'], bins=20)

    for k, v in sco_map.items():
        plt.hist(v, bins=20)

    plt.show()


def calc_rank(lst, score):
    rank = 0
    for i in range(len(lst)):
        if lst[i] >= score:
            rank = i + 1
            
    return rank


def calc_dev(lst, score):
    avr = sum(lst) / len(lst)
    s_dev = 0
    dev = 0
    for v in lst:
        s_dev += (v - avr) ** 2
    s_dev = math.sqrt(s_dev / len(lst))
    if s_dev != 0:
        dev = (score - avr) / s_dev * 10 + 50

    return avr, s_dev, dev


if __name__ == '__main__':
    #analyze_hds()
    analyze_otrs('./data/akutagawa.json')
