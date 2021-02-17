import sys
import random
import numpy as np

class Node():
    def __init__(self,name,level):
        self.name = name
        self.level = level
        self.parent = ''
        self.children = []
        self.siblings = []
        self.meetings = []
        self.meetings_utils = []
        self.time_slots_utils = []

def nodes_per_level(tree,level):
    nodes = 0 
    for node in tree:
        if(node.level == level):
            nodes += 1
    return nodes

def construct_tree(agents):
    tree = []
    tmp_name_index = 2
    level = 1

    root_node = Node('1',0)
    tree.append(root_node)
    agents -= 1

    while agents > 0:
        previous_level_nodes = nodes_per_level(tree,level-1)
        nodes_level = previous_level_nodes * (level+1)
        for i in range(tmp_name_index,tmp_name_index+nodes_level):
            if agents > 0:
                tmp_node = Node(f'{i}',level)
                tree.append(tmp_node)
                agents -= 1
                tmp_name_index += 1
            else:
                break
        level += 1
        
    child_idx = 1
    for node in tree:
        try:
            for j in range(child_idx,child_idx+node.level+2):
                child = tree[j]
                node.children.append(child)
                child_idx = j + 1
        except:
            pass
    for node in tree:
        for child in node.children:
            child.parent = node
    for node_x in tree:
        for node_y in tree:
            if((node_x.parent == node_y.parent) and (node_y.name!= node_x.name)):
                node_x.siblings.append(node_y)
    return tree

def generate_grp(tree,grp_names,max_meetings):
    grp_meetings = []
    nodes_chosen = []
    potential_nodes = []
        
    for node in tree:
        if(len(node.children)):
            potential_nodes.append(node)
    for grp_name in grp_names:
        fl = False
        while(fl==False):
            rnd_node = random.choice(potential_nodes)
            priority_nodes = []
            for node in potential_nodes:
                if(len(node.meetings)==0):
                    priority_nodes.append(node)
            if(priority_nodes):
                rnd_node = random.choice(priority_nodes)
            if(rnd_node in nodes_chosen):
                continue
            tmp_meeting = []
            tmp_meeting.append(rnd_node.name)
            for child in rnd_node.children:
                if(len(child.meetings) > max_meetings):
                    continue
            for child in rnd_node.children:
                child.meetings.append(grp_name)
                tmp_meeting.append(child.name)
            nodes_chosen.append(rnd_node)
            rnd_node.meetings.append(grp_name)
            grp_meetings.append(tmp_meeting)
            fl = True
    return zip(grp_names,grp_meetings)

def generate_ptc(tree,ptc_names,max_meetings):
    ptc_meetings = []
    nodes_chosen = []
    potential_nodes = []
    
    for node in tree:
        if(len(node.children)):
            potential_nodes.append(node)
    for ptc_name in ptc_names:
        fl = False
        while(fl==False):
            rnd_node = random.choice(potential_nodes)
            priority_nodes = []
            for node in potential_nodes:
                if(len(node.meetings)==0):
                    priority_nodes.append(node)
            if(priority_nodes):
                rnd_node = random.choice(priority_nodes)
            if(rnd_node in nodes_chosen):
                continue
            tmp_meeting = []
            tmp_meeting.append(rnd_node.name)
            rnd_child = random.choice(rnd_node.children)
            if(len(rnd_child.meetings) > max_meetings):
                continue
            rnd_node.meetings.append(ptc_name)
            rnd_child.meetings.append(ptc_name)
            nodes_chosen.append(rnd_node)
            tmp_meeting.append(rnd_child.name)
            ptc_meetings.append(tmp_meeting)
            fl = True
    return zip(ptc_names,ptc_meetings)

def generate_sib(tree,sib_names,max_meetings):
    sib_meetings = []
    nodes_chosen = []
    potential_nodes = []
    
    for node in tree:
        if(len(node.siblings)):
            potential_nodes.append(node)
    for sib_name in sib_names:
        fl = False
        while(fl==False):
            rnd_node = random.choice(potential_nodes)
            priority_nodes = []
            for node in potential_nodes:
                if(len(node.meetings)==0):
                    priority_nodes.append(node)
            if(priority_nodes):
                rnd_node = random.choice(priority_nodes)
            if(rnd_node in nodes_chosen):
                continue
            tmp_meeting = []
            tmp_meeting.append(rnd_node.name)
            for sibling in rnd_node.siblings:
                if(len(sibling.meetings) > max_meetings):
                    continue
            for sibling in rnd_node.siblings:
                sibling.meetings.append(sib_name)
                tmp_meeting.append(sibling.name)
            nodes_chosen.append(rnd_node)
            rnd_node.meetings.append(sib_name)
            sib_meetings.append(tmp_meeting)
            fl = True
    return zip(sib_names,sib_meetings)

def generate_utils(tree,time_slots_utils,meetings_utils):
    for node in tree:
        for i in range(len(node.meetings)):
            rnd_ts_util = random.choice(time_slots_utils) 
            node.time_slots_utils = rnd_ts_util
            rnd_meet_util = random.choice(meetings_utils) 
            node.meetings_utils.append(rnd_meet_util)

def print_details(tree,agents,meetings):
    print(f'{"-"*25} INFO: {"-"*25}')
    for x in tree:
        print(f'Info for node {x.name}:')
        if(x.parent):
            print(f'Parent of {x.name}: {x.parent.name}', end = '\n')
        else:
            print(f'Parent of {x.name}: Root node - no parents', end = '\n')
        print(f'Children of {x.name}:',end = ' ')
        if(x.children):
            for idx,child in enumerate(x.children):
                if(idx == len(x.children)-1):
                    print(child.name,end = '\n')
                    break
                print(child.name,end = ', ')
        else:
            print(f'Leaf node - no children', end = '\n')
        print(f'Siblings of {x.name}:',end = ' ')
        if(x.siblings):
            for idx,sibling in enumerate(x.siblings):
                if(idx == len(x.siblings)-1):
                    print(sibling.name,end = '\n')
                    break
                print(sibling.name,end = ', ')
        else:
            print(f'No siblings', end = '\n')
        print(f'Meetings of {x.name} :',end = ' ')
        if(x.meetings):
            for idx,meeting in enumerate(x.meetings):
                if(idx == len(x.meetings)-1):
                    print(f'{meeting} -  Util: {x.meetings_utils[idx]}', end = '\n')
                    break
                print(f'{meeting} - Util: {x.meetings_utils[idx]},', end = ' ')
        else:
            print(f'{x.name} participates in no meetings', end = '\n')
        print(f'Time slots preferences of {x.name} - {x.time_slots_utils}',end = ' ')
        print('\n')

def export_to_file(tree,agents,meetings):
    with open("output.txt", "w") as text_file:
        print(f'{agents},{meetings},{meetings}',file=text_file)
        for node in tree:
            for idx,meeting in enumerate(node.meetings):
                print(f'{node.name},{meeting},{node.meetings_utils[idx]}',file=text_file)
        for node in tree:
            for idx,ts_util in enumerate(node.time_slots_utils):
                print(f'{node.name},{idx+1},{ts_util}',file=text_file)

def dimes_generator():
    agents = int(sys.argv[1])
    meetings = int(sys.argv[2])
    tree = construct_tree(agents)
    max_meetings = 8
    time_slots_utils = [np.arange(10,40,10),
                        np.arange(30,0,-10),
                        np.full(3,10)
                    ]
    meetings_utils = np.arange(10,110,10)
    meeting_names = np.arange(1,meetings+1)
    split_meeting_names = np.array_split(meeting_names,3)
    grp_names, ptc_names, sib_names = split_meeting_names
    grp = generate_grp(tree,grp_names,max_meetings)
    sib = generate_sib(tree,sib_names,max_meetings)
    ptc = generate_ptc(tree,ptc_names,max_meetings)
    generate_utils(tree,time_slots_utils,meetings_utils)

    #sanity check
    # print_details(tree,agents,meetings)

    export_to_file(tree,agents,meetings)



