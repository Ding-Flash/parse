import pandas as pd
import numpy as np
import math
from sklearn.preprocessing import scale
from htrace import Parse
import prettytable as pt

def bfs_tree(tree, nodes):
    res = []
    names = nodes[tree]['name']
    layers = [tree]
    res.append([names])
    while len(layers):
        temp_names = []
        temp_layer = []
        for l in layers:
            for c in nodes[l]['childs']:
                temp_layer.append(c)
                temp_names.append(nodes[c]['name'])

        layers = temp_layer
        res.append(temp_names)

    names = [frozenset(n) for n in res]
    return hash(tuple(names))


def hash_tree(trace):
    trace.build_tree()
    res = [bfs_tree(tree, trace.nodes) for tree in trace.call]
    return len(set(res))


def eu_dist(always: Parse, prefix, sub, s2):
    src_df = pd.read_csv(prefix+'/a/1.csv').drop([0, 4, 6, 3, 7, 5])
    com_df = pd.read_csv(prefix+sub+s2+'.csv').drop([0, 4, 6, 3, 7, 5])
    v1, v2 = [], []
    for name in always.names:
        if always.func_feature[name]['count'] < 2:
            continue
        v1.append(src_df[name][1])
        v1.append(src_df[name][2])
        if name in com_df.columns:
            v2.append(com_df[name][1])
            v2.append(com_df[name][2])
        else:
            v2.extend([0,0])
    v1, v2 = np.array(v1), np.array(v2)
    v1, v2 = scale(v1), scale(v2)
    res = np.linalg.norm(v1 - v2)
    return res


# def eu_dist(always: Parse, prefix, sub, s2):
#     src_df = pd.read_csv(prefix+'/a/1.csv').drop([0, 4, 6, 3, 7, 5])
#     com_df = pd.read_csv(prefix+sub+s2+'.csv').drop([0, 4, 6, 3, 7, 5])
#     v1, v2 = [], []
#     for name in always.names:
#         if always.func_feature[name]['count'] < 2:
#             continue
#         v1.append([src_df[name][1], src_df[name][2]])
#         if name in com_df.columns:
#             v2.append([com_df[name][1], com_df[name][2]])
#         else:
#             v2.append([0,0])
#     v1, v2 = np.array(v1), np.array(v2)
#     v1, v2 = scale(v1), scale(v2)
#     res = np.linalg.norm(v1 - v2)
#     return res


def entropy(prefix, sub, s2):
    src = pd.read_csv(prefix+'/a/1.csv')
    t = pd.read_csv(prefix+sub+s2+'.csv')
    proba = np.array([0]*len(src.columns[1:]))
    count = 0
    for idx, name in enumerate(src.columns[1:]):
        if name in t.columns:
            proba[idx] = t[name][0]
            count += proba[idx]
    proba = proba/count
    res = 0.0
    for p in proba:
        if p:
            res -= p * math.log2(p)
    return res

def delay(path, samplers):
    """
    从trace.log读取信息
    """
    info = {
        'time': [],
        'through': [],
        'ctime': [],
        'cthrough': []
    }
    btime,  bthrough = 0, 0
    with open(path+'/n/trace.log', 'r') as f:
        line = f.readlines()[-1]
        _, btime, _, bthrough = line.split(' ')
        btime = float(btime)
        bthrough = float(bthrough)
    tb = pt.PrettyTable()
    tb.field_names = ['bench', '时间', '吞吐量']
    tb.add_row([path, btime, bthrough])
    print(tb)
    for s in samplers:
        with open(path+s+'/trace.log', 'r') as f:
            line = f.readlines()[-1]
            _, time, _, through = line.split(' ')
            time = float(time)
            through = float(through)
        info['time'].append(time)
        info['through'].append(through)
        info['ctime'].append((time-btime)/btime)
        info['cthrough'].append((through-bthrough)/bthrough)
    return info


def merge_info_display(path, samplers):
    data = pd.read_csv(path+'res.csv')
    another = delay(path, samplers)
    data['time'] = another['time']
    # data['ctime'] = another['ctime']
    data['through'] = another['through']
    # data['cthrough'] = another['cthrough']
    data['size'] = data['size'].apply(lambda x: x/(2**20))
    data.drop(['Unnamed: 0'], axis=1, inplace=True)
    data.index = ['全采样', '限速采样', '令牌桶采样', '概率采样(0.01)', '概率采样(0.1)']
    data = data.reindex(index = ['全采样', '概率采样(0.1)', '限速采样', '令牌桶采样', '概率采样(0.01)'])
    data.columns = ['函数种类', '调用树种类', '相似度(欧氏)', '信息熵', '文件大小(M)', '执行时间',
    #  'time延迟率', 
     '吞吐量', 
    #  'through降低率'
     ]
    return data

def merge_info(path, samplers):
    data = pd.read_csv(path+'res.csv')
    another = delay(path, samplers)
    data['time'] = another['time']
    data['ctime'] = another['ctime']
    data['through'] = another['through']
    data['cthrough'] = another['cthrough']
    data['size'] = data['size'].apply(lambda x: x/(2**20))
    data.drop(['Unnamed: 0'], axis=1, inplace=True)
    data.index = ['always', 'bump', 'tbuck', 'p0.01', 'p0.1']
    data = data.reindex(index = ['always', 'p0.01', 'p0.1', 'bump', 'tbuck'])
    return data