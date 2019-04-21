from htrace import Parse
from util import *
import pandas as pd
import prettytable as pt

from conf import *

always = Parse(bench + '/a/1.out', flag)

com = {
    'node': [],
    'tree': [],
    'dist': [],
    'en': []
}


def sampler2csv(sub_path, flag):
    res = {
        'node': [],
        'tree': [],
        'dist': [],
        'en': []
    }
    display = []
    for i in range(number):
        print(f"分析{sub_path}{i+1}.out....")
        temp = Parse(bench+sub_path+str(i+1)+'.out', flag)
        temp.df.to_csv(bench+sub_path+str(i+1)+'s.csv')
        print(f"分析{sub_path}{i+1}.out结束")
        node_number = len(temp.names)
        tree_number = hash_tree(temp)
        dist = eu_dist(always, bench, sub_path, str(i+1))
        en = entropy(bench, sub_path, str(i+1))
        res['node'].append(node_number)
        res['tree'].append(tree_number)
        res['dist'].append(dist)
        res['en'].append(en)
        display.append([i+1, node_number, tree_number, dist, en])
    tb = pt.PrettyTable()
    tb.field_names = [sub_path[:-1], 'node', 'tree', 'dist', 'entropy']
    for row in display:
        tb.add_row(row)
    print(tb)
    info = pd.DataFrame(res)
    desc = info.describe()
    com['node'].append(desc['node']['mean'])
    com['tree'].append(desc['tree']['mean'])
    com['dist'].append(desc['dist']['mean'])
    com['en'].append(desc['en']['mean'])
    desc.to_csv(bench+sub_path+"info_desc.csv")
    info.to_csv(bench+sub_path+"info.csv")


def main():
    for sampler in samplers:
        sampler2csv(sampler, flag)
    c = pd.DataFrame(com)
    c.index = [s[:-1] for s in samplers]
    c.to_csv(bench + 'res.csv')


if __name__ == "__main__":
    main()
