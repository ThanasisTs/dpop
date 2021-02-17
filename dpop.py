import sys
import yaml
import numpy as np
import pandas as pd
import itertools
import copy
import random
import time
import csv

num_agents, num_meetings, max_msg_size, start_time = 0, 0, 0, 0

# Node class
class Node():
    def __init__(self, name, potential_values):
        self.name = name
        self.parent = None
        self.children = []
        self.p_parents = []
        self.sep = []
        self.relations = {}
        self.util = pd.DataFrame({})
        self.potential_values = potential_values
        self.values_based_on_parent_values = None
        self.value = None
        self.children_utils = None

    def set_parent(self, other):
        self.parent = other

    def set_children(self, other):
        self.children.append(other)

    def set_p_parents(self, other):
        self.p_parents.append(other)

    def set_sep(self, other):
        self.sep.append(other)

    def set_relations(self, other, relation):
        self.relations.update({other: relation})


def project_out(node, join_matrix):
    global max_msg_size
    start_time = time.time()
    headers = list(join_matrix.columns)
    headers.remove(node.name)
    headers.remove('Util')
    tmp = join_matrix.copy()
    tmp2 = tmp.sort_values(
        'Util', ascending=False).drop_duplicates(headers)
    project_out_df = tmp2.copy()
    del project_out_df[node.name]
    del tmp2['Util']
    values_based_on_ancestor_values = tmp2
    values_based_on_ancestor_values = values_based_on_ancestor_values.rename(columns={
        node.name: 'Value'})

    if len(values_based_on_ancestor_values) > max_msg_size:
        max_msg_size = len(values_based_on_ancestor_values)

    # print("Project out --- %s seconds ---" % (time.time() - start_time))
    return project_out_df.reset_index(drop=True), values_based_on_ancestor_values.reset_index(drop=True)


def join(node, relations, flag):
    if node.name == '15,5':
        print(relations)
        input()
    start_time = time.time()
    join_dict = {}
    headers = []
    for i in relations:
        headers.extend(list(i.columns))
    headers = list(set(headers))
    headers.remove('Util')
    headers.append('Util')
    value_combs_join = list(itertools.product(node.potential_values, repeat=len(headers)-1))
    for i in range(len(headers)-1):
        join_dict.update({headers[i]: list(zip(*value_combs_join))[i]})
    join_df = pd.DataFrame(join_dict)

    join_df['Util'] = 0
    for relation in relations:
        tmp = list(relation.columns)
        tmp.remove('Util')
        join_df = pd.merge(join_df, relation, how='left', on=tmp)
        join_df['Util_x'] = join_df['Util_x'] + join_df['Util_y']
        join_df.drop(['Util_y'], axis=1, inplace=True)
        join_df = join_df.rename(columns={'Util_x': 'Util'})

    if flag:
        # print("Join --- %s seconds ---" % (time.time() - start_time))
        return project_out(node, join_df)
    else:
        # print("Join --- %s seconds ---" % (time.time() - start_time))
        return join_df.reset_index(drop=True)


def dpop(tree):
    global max_msg_size, num_agents, num_messages, start_time

    # visited: set to keep track of all visited nodes
    visited = set()

    # open_set: list to keep track of nodes to be processed
    open_set = []
    for node in tree:
        if not node.children:
            open_set.append(node)

    # Util propagation
    print('--- Util propagation ---')
    while open_set:
        current_node = open_set[0]

        # If the current node is the root, exit util propagation phase
        if current_node.parent is None:
            if len(visited) == len(tree) - 1:
                if len(current_node.children) == 1:
                    current_node.util = current_node.children[0].util
                    break
                tmp = [child.util for child in current_node.children]
                current_node.util = join(current_node, tmp, False)
                break
            else:
                del open_set[0]
                open_set.append(current_node)
                continue

        # If the node is a leaf, compute its utility
        if not current_node.children:
            current_node.util, current_node.values_based_on_parent_values = join(
                current_node, current_node.relations.values(), True)
        
        # If the node is not a leaf, make sure that the utilities of its children are
        # available and then compute its utility
        else:
            children_update = True
            for child in current_node.children:
                if child.util.empty:
                    open_set.remove(current_node)
                    open_set.append(current_node)
                    children_update = False
                    break
            if not children_update:
                continue
            else:
                # If the children utilities are available,
                # join their util messages and compute the node's final utility
                children_utils = [
                    child.util for child in current_node.children]
                current_node.children_utils = join(
                    current_node, children_utils, False)
                tmp = list(current_node.relations.values())
                tmp.append(current_node.children_utils)
                current_node.util, current_node.values_based_on_parent_values = join(
                    current_node, tmp, True)


        # Remove current node from open_set and add its parent
        if current_node.parent not in open_set:
            open_set.append(current_node.parent)
        open_set.remove(current_node)
        visited.add(current_node.name)

    num_util_msgs = len(tree)-1
    num_value_msgs = len(tree)-1
    num_variables = len(tree)
    num_cycles, num_constraints = 0, 0
    for node in tree:
        num_value_msgs += len(node.p_parents)
        num_cycles += len(node.p_parents)
    num_constraints = num_cycles + len(tree) -1
    num_messages = num_value_msgs + num_util_msgs


    print("Number of constraints: {}".format(num_constraints))

    print("Number of cycles: {}".format(num_cycles))

    print("Number of messages: {}".format(num_messages))

    print("Maximum message size: {}".format(max_msg_size))
    # Value propagation
    print('--- Value propagation ---')

    value_prop_start_time = time.time()
    open_set = [node for node in tree]

    # Node values
    node_values = {}

    sorted_root_util = current_node.util.sort_values('Util', ascending=False)
    node_values.update(
        {current_node.name: sorted_root_util[current_node.name][0]})
    current_node.value = list(node_values.values())[0]
    open_set.remove(current_node)

    next_node = True

    # For each node, get the value of its parent (and pseudoparents) and compute its own value
    while open_set:
        if not current_node.parent:
            current_node = random.choice(current_node.children)
        for ancestor in current_node.sep:
            if ancestor.name not in node_values.keys():
                open_set.remove(current_node)
                open_set.append(current_node)
                current_node = open_set[0]
                next_node = False
                break
        if not next_node:
            next_node = True
            if open_set == []:
                break
            else:
                continue
        headers = list(current_node.values_based_on_parent_values.columns)
        headers.remove('Value')
        df = current_node.values_based_on_parent_values
        for h in headers:
            df = df[(df[h] == node_values.get(h))]
        df = df.reset_index(drop=True)
        node_values.update({current_node.name: df['Value'][0]})
        current_node.value = df['Value'][0]
        open_set.remove(current_node)
        try:
            current_node = open_set[0]
        except:
            break
    print("Value propagation --- %s seconds ---" % (time.time() - value_prop_start_time))

    # Print the nodes with their final values
    for node in tree:
        print(node.name, node.value)

    print("Total Time --- %s seconds ---" % (time.time() - start_time))
    csvFile = open('results.csv', 'a')
    wr = csv.writer(csvFile)
    wr.writerow([sys.argv[1].split('/')[1][:-9], num_agents, num_meetings, num_variables, num_constraints, num_messages, max_msg_size, num_cycles, round(time.time()-start_time, 2)])

def main():
    global num_agents, num_meetings, start_time
    start_time = time.time()

    num_agents = int(sys.argv[1].split('/')[1].split('_')[0])
    num_meetings = int(sys.argv[1].split('/')[1].split('_')[1])

    # Parse the yaml and create the tree
    tree_file = yaml.load(open(sys.argv[1], 'r'), Loader=yaml.FullLoader)

    tree = []
    tree_dict = {}
    for node in tree_file['nodes']:
        tree_node = Node(node, tree_file['potential_values'])
        tree.append(tree_node)
        tree_dict.update({node: tree_node})

    for node in tree:
        if tree_file['parents'][node.name] is not None:
            node.set_parent(tree_dict.get(tree_file['parents'][node.name][0]))
            node.set_relations(
                node.parent, tree_file['parent_relations'][node.name])

        if tree_file['children'][node.name] is not None:
            for child in tree_file['children'][node.name]:
                node.set_children(tree_dict.get(child))

        if tree_file['p_parents'][node.name] is not None:
            for p_parent in tree_file['p_parents'][node.name]:
                node.set_p_parents(tree_dict.get(p_parent))
                node.set_relations(tree_dict.get(
                    p_parent), tree_file['pseudo_parent_relations'][node.name][p_parent])

        if tree_file['sep'][node.name] is not None:
            for sep in tree_file['sep'][node.name]:
                node.set_sep(tree_dict.get(sep))

    for node in tree:
        value_combs_ancestors = list(itertools.product(node.potential_values, repeat=2))
        break

    for node in tree:
        t = {}
        for k, v in node.relations.items():
            tmp = {node.name: list(zip(*value_combs_ancestors))[0]}
            tmp.update({k.name: list(zip(*value_combs_ancestors))[1]})
            a = []
            for ja in v:
                for i in ja:
                    a.append(i)
            tmp.update({'Util': a})
            t.update({k: pd.DataFrame(tmp)})
        node.relations = t

    # call DPOP algorithm
    dpop(tree)

if __name__ == "__main__":
    main()
