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
    elif '(' in name:
        return name[:name.find('(')]
    else:
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

    def __init__(self, path, all_nodes):
        self.traces = Trace(path)
        self.patt_str = '\\{"a":.*?[(\\])|(\\})]\\}'
        self.path = path
        self.size = os.path.getsize(path)
        self.patt = re.compile(self.patt_str)
        self.res = []
        self.call = []
        self.nodes = defaultdict(produce)
        self.names = []
        self.trees = []
        self.func_feature = None
        self.df = None
        self.loads()
        self.parse_nodes()
        self.build_df(all_nodes=all_nodes)

    def loads(self):
        """
        使用正则解析trace文件，将每个节点条目存到res列表中
        :return:
        """
        for line in tqdm(self.traces):
            self.res.extend([json.loads(tree) for tree in self.patt.findall(line)])

    def parse_nodes(self):
        """
        清理res中每个节点条目的信息，并根据 parent 键 构造父子关系
        :return:
        """
        for func in self.res:
            cur = self.nodes[func['a']]
            if not cur['name']:
                cur['name'] = clean_name(func['d'])
                cur['time'] = func['e'] - func['b']
                cur['begin'] = func['b']
                cur['end'] = func['e']
            if not len(func['p']):
                self.call.append(func['a'])
                continue
            for p_hash in func['p']:
                parent = self.nodes[p_hash]
                parent['childs'].append(func['a'])

    def build_df(self, all_nodes=False):
        """
        将数据转化为dataframe
        :param all_nodes: 是否统计所有节点
        :return:
        """
        if all_nodes:
            root_nodes = list(self.nodes.values())
        else:
            root_nodes = [self.nodes[hash_node] for hash_node in self.call]
        nodes_info = {'name': [], 'time': [], 'begin': [], 'end': []}
        for root in root_nodes:
            name = root['name']
            if name is None:
                continue
            name = clean_name(root['name'])
            nodes_info['name'].append(name)
            nodes_info['time'].append(root['time'])
            nodes_info['begin'].append(root['begin'])
            nodes_info['end'].append(root['end'])

        self.df = pd.DataFrame(nodes_info)
        self.names = self.df['name'].value_counts().index
        self.extra_feature()

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
                callTree['childs'].append({'hash': child,
                                           'name': self.nodes[child]['name'],
                                           'childs': []})
                deep_call(child, callTree['childs'][-1])

        for root in tqdm(self.call):
            self.trees.append({'hash': root,
                               'name': self.nodes[root]['name'],
                               'childs': []})
            deep_call(root, self.trees[-1])

    def extra_feature(self):
        if self.names is None:
            raise Exception
        data = []
        for name in self.names:
            data.append(self.df[self.df.name == name].describe().time)

        self.func_feature = pd.concat(data, axis=1)
        self.func_feature.columns = self.names
        self.func_feature = self.func_feature.fillna(0)
        self.func_feature.to_csv(self.path[:-4] + '.csv')
