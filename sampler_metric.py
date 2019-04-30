from htrace import Parse
import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from util import merge_info

sns.set(style="whitegrid")

data_path={
    'dfsioe_r': 'data/dfsioe_r/',
    'dfsioe_w': 'data/dfsioe_w/',
    'kmeans': 'data/kmeans/',
    'pagerank': 'data/pagerank/',
    'terasort': 'data/terasort/',
    'wordcount': 'data/wordcount/'
}
samplers = ['a', 'l', 't', 'p0.01', 'p0.1']

def draw_chart(test):
    fig, axes = plt.subplots(2, 3, figsize = (12, 12))
    node = sns.barplot(x=test.index, y=test.node, ax=axes[0,0])
    node.set(xlabel='Function type',ylabel='kind of function')
    tree = sns.barplot(x=test.index, y=test.tree, ax=axes[0,1])
    tree.set(xlabel='Trace tree type',ylabel='kind of trace tree')
    en = sns.barplot(x=test.index, y=test.en, ax=axes[0,2])
    en.set(xlabel='Information entropy',ylabel='entropy')
    dist = sns.barplot(x=test.index, y=test.dist, ax=axes[1,0])
    dist.set(xlabel='Similarity',ylabel='euclidean distance')
    time = sns.barplot(x=test.index, y=test.time, ax=axes[1,1])
    time.set(xlabel='Execution time',ylabel='time(s)')
    test['size'] = [0]+test['size'].tolist()[1:]
    i = ['']+test.index.tolist()[1:]
    size = sns.barplot(x=i, y=test['size'], ax=axes[1,2])
    size.set(xlabel='Trace File Size',ylabel='file size(MB)')
    plt.subplots_adjust(wspace=0.3, hspace=0.2)
# dfsioe_r = merge_info('data/dfsioe_r/', samplers)
# draw_chart(dfsioe_r)

terasort = merge_info('data/kmeans/', samplers)
draw_chart(terasort)

plt.show()