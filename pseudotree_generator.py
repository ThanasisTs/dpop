import sys
import random
import numpy as np


def handle_incoming_tokens(node,visited,dfs):
	if not dfs:
		dfs.append(node)
		visited.append(node)
	else:
		node.parent.append(dfs[-1])
		dfs[-1].children.append(node)
		for neighbor in node.neighbors:
			if neighbor in dfs and neighbor not in node.parent:
				node.p_parents.append(neighbor)
		dfs.append(node)
	while True:
		count = 0
		max_length = len(node.neighbors)
		for neighbor in node.neighbors:
			if neighbor not in visited:
				node = neighbor
				visited.append(node)
				break
			count += 1
		if count == max_length:
			dfs.remove(node)
			break
		else:
			handle_incoming_tokens(node,visited,dfs)
			node = node.parent[0]


def pseudotree_generator(graph):
	visited = []
	dfs = []
	root = random.choice(graph)
	handle_incoming_tokens(root,visited,dfs)
	
	if len(visited) == len(graph):
		print("Consistent graph")
		return True, graph
	else:
		print("Inconsistent graph")
		return False, graph
		







