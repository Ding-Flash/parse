import pandas as pd
import numpy as np
from htrace import Parse
from sklearn.preprocessing import scale


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


def eu_dist(src: Parse, s1, s2):
    res = 0.0
    src_df = pd.read_csv(prefix+s1+'.out.csv').drop([0,4,6,3,7,5])
    com_df = pd.read_csv(prefix+s2+'.out.csv').drop([0,4,6,3,7,5])
    v1, v2 = [], []
    for name in src.names:
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


def entropy(src: Parse,file):
    t = pd.read_csv(prefix+file+'.out.csv')
    proba = np.array([0]*len(src.names))
    count = 0
    for idx, name in enumerate(src.names):
        if name in t.columns:
            proba[idx] = t[name][0]
            count += proba[idx]
    print(count)
    proba = proba/count
    res = 0.0
    for p in proba:
        if p:
            res -= p * math.log2(p)
    return res