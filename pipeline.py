from dimes_generator import dimes_generator
from graph_generator import graph_generator
from pseudotree_generator import  pseudotree_generator
from yaml_generator import yaml_generator

consistent = False
while(not consistent):
    dimes_generator()
    graph = graph_generator()
    consistent, pseudotree = pseudotree_generator(graph)
    yaml_generator(pseudotree)