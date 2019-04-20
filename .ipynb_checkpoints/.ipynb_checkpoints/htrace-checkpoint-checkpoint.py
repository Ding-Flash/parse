import os
import re
import json
from tqdm import tqdm
import pandas as pd
from collections import defaultdict


def produce():
    return {
        'name': None,
        'time': None,
        'begin': None,
        'end': None,
        'childs': []
    }


def clean_name(name):
    if '[' in name:
        return name[:name.find('[')]
    if '(' in name:
        return name[:name.find('(')]
    return name


class Trace:
    
    def __init__(self, path):
        self.path = path
        
    def __iter__(self):
        f = open(self.path)
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                f.close()
                return


class Parse:
    
    def __init__(self, path):
        self.traces = Trace(path)
        self.patt_str = r'\{"a":.*?[(\])|(\})]\}'
        self.path = path
        self.size = os.path.getsize(path)
        self.patt = re.compile(self.patt_str)
        self.res = []
        self.call = []
        self.nodes = defaultdict(produce)
        self.trees = []
        self.df = None
        self.loads()
        self.name = None
        self.parse_nodes()
        
    def loads(self):
        """
        使用正则解析trace文件，将每个节点条目存到res列表中
        :return:
        """
        for line in tqdm(self.traces):
            self.res.extend(
                [json.loads(tree) for tree in self.patt.findall(line)]
            )

    def parse_nodes(self):
        """
        清理res中每个节点条目的信息，并根据 parent 键 构造父子关系
        :return:
        """
        for func in self.res:
            cur = self.nodes[func['a']]
            if not cur['name']:
                cur['name'] = func['d']
                cur['time'] = func['e'] - func['b']
                cur['begin'] = func['b']
                cur['end'] = func['e']

            if not len(func['p']):
                self.call.append(func['a'])
                continue

            for p_hash in func['p']:
                parent = self.nodes[p_hash]
                parent['childs'].append(func['a'])

    def build_df(self, clean=True, all_nodes=False):
        """
        将数据转化为dataframe
        :param clean: 统计时一些函数名会自带一些参数，导致原本同一个函数会当成不同的函数，True: 表示对这些函数当成同一个函数处理，False: 表示当成不同的函数处理
        :param all_nodes: 是否统计所有节点
        :return:
        """
        if all_nodes:
            root_nodes = list(self.nodes.values())
        else:
            root_nodes = [self.nodes[hash_node] for hash_node in self.call]
        nodes_info = {
            'name': [],
            'time': [],
            'begin': [],
            'end': []
        }
        for root in root_nodes:
            name = root['name']
            if name is None:
                print(root)
                continue
            if clean:
                name = clean_name(root['name'])
            nodes_info['name'].append(name)
            nodes_info['time'].append(root['time'])
            nodes_info['begin'].append(root['begin'])
            nodes_info['end'].append(root['end'])
        self.df = pd.DataFrame(nodes_info)
        self.name = self.df['name'].value_counts().index
        return self.df

    def build_tree(self):
        """
        构建函数调用树
        :return:
        """
        if not len(self.call):
            self.parse_nodes()

        def deep_call(root, callTree):
            if not len(self.nodes[root]['childs']):
                return
            for child in self.nodes[root]['childs']:
                callTree['childs'].append({
                    "hash": child,
                    "name": self.nodes[child]['name'],
                    "childs": []
                })
                deep_call(child, callTree['childs'][-1])

        for root in tqdm(self.call):
            self.trees.append({
                "hash": root,
                "name": self.nodes[root]['name'],
                "childs": []
            })
            deep_call(root, self.trees[-1])


def compress(node, desc, deep, layer):
    layer = layer + "&" + str(deep)
    # vis = set()
    for index, child in enumerate(node['childs']):
        name = child['name']
        if '[' in child['name']:
            name = child['name'][:child['name'].find('[')]
        if '(' in child['name']:
            name = child['name'][:child['name'].find('(')]
        # if name in vis:
        #     continue
        # vis.add(name)
        desc['d'] = desc['d'] + '->' + layer + "#" + str(index) + '(' + name + ')'
        compress(child, desc, deep+1, layer + "#" + str(index))


def hash_tree(trees):
    hashtree = []
    for tree in trees:
        name = tree['name']
        if '[' in tree['name']:
            name = tree['name'][:tree['name'].find('[')]
        if '(' in tree['name']:
            name = tree['name'][:tree['name'].find('(')]
        desc = {'d': '0'+'('+name+')'}
        compress(tree, desc, 1, '0')
        hashtree.append(desc['d'])
    return hashtree


