import pandas as pd
import numpy as np
import math
from sklearn.preprocessing import scale
from htrace import Parse


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
    src_df = pd.read_csv(prefix+'a.csv').drop([0,4,6,3,7,5])
    com_df = pd.read_csv(prefix+sub+s2+'.csv').drop([0,4,6,3,7,5])
    v1, v2 = [], []
    for name in always.names:
        if always.func_feature[name]['count'] < 10:
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


def entropy(prefix, sub, s2):
    src = pd.read_csv(prefix+'a.csv')
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