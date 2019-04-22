from htrace import Parse
from util import *
import pandas as pd
import prettytable as pt
from time import strftime

from conf import *


def fprint(info):
    print(strftime('[%H:%M:%S]'), end=' ')
    print(info)


def sampler2csv(sub_path, flag, always, bench, com):
    res = {
        'node': [],
        'tree': [],
        'dist': [],
        'en': [],
        'size': []
    }
    display = []
    for i in range(number):
        fprint(f"分析{sub_path}{i+1}.out....")
        temp = Parse(bench+sub_path+str(i+1)+'.out', flag)
        temp.df.to_csv(bench+sub_path+str(i+1)+'s.csv')
        fprint(f"分析{sub_path}{i+1}.out结束")
        node_number = len(temp.names)
        tree_number = hash_tree(temp)
        dist = eu_dist(always, bench, sub_path, str(i+1))
        en = entropy(bench, sub_path, str(i+1))
        size = temp.size
        res['node'].append(node_number)
        res['tree'].append(tree_number)
        res['dist'].append(dist)
        res['en'].append(en)
        res['size'].append(size)
        display.append([i+1, node_number, tree_number, dist, en, size])
    info = pd.DataFrame(res)
    desc = info.describe()
    com['node'].append(desc['node']['mean'])
    com['tree'].append(desc['tree']['mean'])
    com['dist'].append(desc['dist']['mean'])
    com['en'].append(desc['en']['mean'])
    com['size'].append(desc['size']['mean'])
    desc.to_csv(bench+sub_path+"info_desc.csv")
    info.to_csv(bench+sub_path+"info.csv")


def main():
    for bench in benchs:
        com = {
            'node': [],
            'tree': [],
            'dist': [],
            'en': [],
            'size': []
        }
        fprint('-------------------------------')
        fprint(f'{bench} running....')
        always = Parse(bench + '/a/1.out', flag)
        always.df.to_csv(bench+'/a/1s.csv')
        for sampler in samplers:
            sampler2csv(sampler, flag, always, bench, com)
        c = pd.DataFrame(com)
        c.index = [s[:-1] for s in samplers]
        c.to_csv(bench + 'res.csv')
        fprint('--------------------------------')


if __name__ == "__main__":
    main()
