from htrace import Parse
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools
from util import delay
import math

data_path = {
    'dfsioe_read': 'ndata/dfsioe_r/',
    'dfsioe_write': 'ndata/dfsioe_w/',
    'terasort': 'ndata/terasort/',
    'wordcount': 'ndata/wordcount/',
    'kmeans': 'ndata/kmeans/',
    'pagerank': 'ndata/pagerank/'
}
samplers = ['a', 'l', 't', 'p0.1', 'p0.01']


def merge_info(bench, samplers):
    path = data_path[bench]
    data = pd.read_csv(path + 'res.csv')
    another = delay(path, samplers)
    data['bench'] = bench
    data['time'] = [math.log(a) for a in another['time']]
    data['ctime'] = [a * 100 for a in another['ctime']]
    data['through'] = another['through']
    data['cthrough'] = another['cthrough']
    data['filesize'] = data['size'].apply(lambda x: x / (2 ** 20))
    data.drop(columns=['size'], inplace=True)

    data.drop(['Unnamed: 0'], axis=1, inplace=True)
    data.index = ['always', 'bump', 'tbuckt', 'p0.1', 'p0.01']
    data = data.reindex(index=['always', 'p0.01', 'p0.1', 'bump', 'tbuckt'])
    data['node'] = data['node'] / data['node']['always']  # 和全采样的相除
    data['tree'] = data['tree'] / data['tree']['always']  # 和全采样的相除
    data['filesize'] = (data['filesize'] / data['filesize']['always']) * 100  # 和全采样的相除
    data['filesize'] = [math.log(d) for d in data['filesize']]
    data['sampler'] = data.index
    return data


temp = [merge_info(k, samplers) for k, v in data_path.items()]
benchs = pd.concat(temp)

benchs = benchs.drop(columns=['sampler'])
benchs['sampler'] = benchs.index

bnode = benchs.loc[:, ['node', 'bench', 'sampler']]
btree = benchs.loc[:, ['tree', 'bench', 'sampler']]
ben = benchs.loc[:, ['en', 'bench', 'sampler']]
bdist = benchs.loc[:, ['dist', 'bench', 'sampler']]
btime = benchs.loc[:, ['ctime', 'time', 'bench', 'sampler']]
bsize = benchs.loc[:, ['filesize', 'bench', 'sampler']]

sns.set(style="whitegrid", color_codes=True)
fig, axes = plt.subplots(3, 2, figsize=(12, 6))

hatches = itertools.cycle(['', '//', '\\\\', '..', '--'])

# time
time_plt = sns.barplot(x=btime.bench, y=btime.time, hue=btime.sampler, ax=axes[0,0], linewidth=0.7)
# time_plt.legend(loc=2, bbox_to_anchor=(1.01, 1.0), borderaxespad=0.)

for i, bar in enumerate(time_plt.patches):
    if i % 6 == 0:
        hatch = next(hatches)
    bar.set_hatch(hatch)


time_plt.legend().remove()
time_plt.set(xlabel='Execution Time', ylabel='log(time)')
plt.legend([time_plt], ['sampler'], loc='upper center')
# plt.legend([time_plt],  loc='upper center', bbox_to_anchor=(0.5, 1.5), ncol=5, fancybox=True)

# size
size_plt = sns.barplot(x=bsize.bench, y=bsize.filesize, hue=bsize.sampler, ax=axes[0,1], linewidth=0.7)
size_plt.legend().remove()

for i, bar in enumerate(size_plt.patches):
    if i % 6 == 0:
        hatch = next(hatches)
    bar.set_hatch(hatch)

size_plt.set(xlabel='Trace file size', ylabel='log(size)')


# node
node_plt = sns.barplot(x=bnode.bench, y=bnode.node, hue=bnode.sampler, ax=axes[1,0], linewidth=0.7)
node_plt.legend().remove()

for i, bar in enumerate(node_plt.patches):
    if i % 6 == 0:
        hatch = next(hatches)
    bar.set_hatch(hatch)

node_plt.set(xlabel='Function', ylabel='number of function')
# tree
tree_plt = sns.barplot(x=btree.bench, y=btree.tree, hue=btree.sampler, ax=axes[1,1], linewidth=0.7)
tree_plt.legend().remove()

for i, bar in enumerate(tree_plt.patches):
    if i % 6 == 0:
        hatch = next(hatches)
    bar.set_hatch(hatch)

tree_plt.set(xlabel='Call Tree', ylabel='number of call tree')
# 信息熵
en_plt = sns.barplot(x=ben.bench, y=ben.en, hue=ben.sampler, ax=axes[2,0], linewidth=0.7)
en_plt.legend().remove()

for i, bar in enumerate(en_plt.patches):
    if i % 6 == 0:
        hatch = next(hatches)
    bar.set_hatch(hatch)

en_plt.set(xlabel='Information Entropy', ylabel='entropy')
# 相似度
dist_plt = sns.barplot(x=bdist.bench, y=bdist.dist, hue=bdist.sampler, ax=axes[2,1], linewidth=0.7)
dist_plt.legend().remove()

for i, bar in enumerate(dist_plt.patches):
    if i % 6 == 0:
        hatch = next(hatches)
    bar.set_hatch(hatch)

dist_plt.set(xlabel='Sample Similarity', ylabel='dist')




plt.tight_layout()
fig.savefig('../mc.pdf')
plt.show()
