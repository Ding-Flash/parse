from htrace import Parse
from util import *
import pandas as pd
import prettytable as pt

bench = '/Users/yangs/Desktop/htrace/wordcount/'

samplers = ['limit/', 'number/', 'tbuck/', 'probability/']

flag = True

always = Parse(bench + 'a.out', flag)


def sampler2csv(sub_path, flag):
    res = {
        'node_number': [],
        'tree_number': [],
        'eu_dist': [],
        'entropy': []
    }
    display = []
    for i in range(10):
        print(f"分析{sub_path}{i+1}.out....")
        temp = Parse(bench+sub_path+str(i+1)+'.out', flag)
        print(f"分析{sub_path}{i+1}.out结束")
        node_number = len(temp.names)
        tree_number = hash_tree(temp)
        dist = eu_dist(always, bench, sub_path, str(i+1))
        en = entropy(bench, sub_path, str(i+1))
        res['node_number'].append(node_number)
        res['tree_number'].append(tree_number)
        res['eu_dist'].append(dist)
        res['entropy'].append(en)
        display.append([i+1, node_number, tree_number, dist, en])
    tb = pt.PrettyTable()
    tb.field_names = [sub_path[:-1], 'node', 'tree', 'dist', 'entropy']
    for row in display:
        tb.add_row(row)
    print(tb)
    info = pd.DataFrame(res)
    info.describe().to_csv(bench+sub_path+"info_desc.csv")
    info.to_csv(bench+sub_path+"info.csv")


def main():
    for sampler in samplers:
        sampler2csv(sampler, flag)


if __name__ == "__main__":
    main()
