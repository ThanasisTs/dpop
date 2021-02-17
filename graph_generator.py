import sys
import numpy as np


# Node class
class Node():
	def __init__(self, name, util):
		self.name = name
		self.util = util
		self.neighbors = []
		self.agent_relation = {}
		self.meeting_relation = {}
		self.parent = []
		self.p_parents = []
		self.children = []
		self.p_children = []

	def set_neighbor(self, other):
		self.neighbors.append(other)

	def set_agent_relation(self, other):
		temp = []
		for i in range(len(self.util)):
			row = []
			for j in range(len(other.util)):
				if i == j:
					row.append(-10000000)
				else:
					row.append(int(self.util[i] + other.util[j]))
			temp.append(row)
		self.agent_relation.update({other : temp})

	def set_meeting_relation(self, other):
		temp = []
		for i in range(len(self.util)):
			row = []
			for j in range(len(other.util)):
				if i == j:
					row.append(10000000)
				else:
					row.append(int(self.util[i] + other.util[j]))
			temp.append(row)
		self.meeting_relation.update({other : temp})


def graph_generator():
	file = open(sys.argv[3], 'r')
	fl = file.readlines()
	agent_meetings = {}
	agent = 1
	meetings = []
	first_time = True
	agent_flag = True
	# For each node in the future tree, construct its util vector and 
	# store the result in a dictionary of the form {(agent,meeting) : util} 
	for i in range(len(fl)):
		if i==0:
			num_agents = int(fl[i].split(',')[0])
		elif first_time and (agent_flag or int(fl[i].split(',')[0]) != 1):
			if int(fl[i].split(',')[0]) != 1:
				agent_flag = False
			agent_meetings.update({"{},{}".format(int(fl[i].split(',')[0]), int(fl[i].split(',')[1])) : np.array([int(fl[i].split(',')[2])])})
		else:
			if first_time:
				agent = 1
				first_time = False
				times = np.array([int(fl[i].split(',')[2])])
			else:
				if int(fl[i].split(',')[0]) == agent:
					times = np.append(times, int(fl[i].split(',')[2]))
				else:
					for k,v in agent_meetings.items():
						if int(k.split(',')[0]) == agent:
							agent_meetings.update({k : v*times})
					times = np.array([int(fl[i].split(',')[2])])
					agent = int(fl[i].split(',')[0])
	for k,v in agent_meetings.items():
		if int(k.split(',')[0]) == agent:
			agent_meetings.update({k : v*times})

	# Based on the dictionary, construct the Node objects containing
	# the neighbors and the util matrices with each neighbor
	graph = []
	name_map = {}
	for k in agent_meetings.keys():
		node = Node(k, agent_meetings.get(k))
		name_map.update({k : node})
		graph.append(node)

	for node in graph:
		for k in name_map.keys():
			if node != name_map.get(k):
				if node.name.split(',')[0] == k.split(',')[0] or node.name.split(',')[1] == k.split(',')[1]:
					node.set_neighbor(name_map.get(k))

	for node in graph:
		for neighbor in node.neighbors:
			if node.name.split(',')[0] == neighbor.name.split(',')[0]:
				node.set_agent_relation(neighbor)
			else:
				node.set_meeting_relation(neighbor)

	# if input("Print graph? (y,n): ") == 'y':
	# 	for node in graph:
	# 		print("Node: ", node.name)
	# 		for neighbor in node.neighbors:
	# 			print("Neighbor: ", neighbor.name)
	# 			try:
	# 				print("Agent_relation: ", node.agent_relation[neighbor])
	# 			except:
	# 				print("Meeting_relation: ", node.meeting_relation[neighbor])
	# 		print("==============================================")

	return graph

