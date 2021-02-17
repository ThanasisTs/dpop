import sys
import yaml

def yaml_generator(graph):
	file = open(sys.argv[4]+'.yaml', 'w')
	
	# add nodes
	node_names = [i.name for i in graph]
	yaml_dict = {'nodes' : node_names}
	yaml.dump(yaml_dict, file)
	
	# add parents
	tmp = {}
	for node in graph:
		try:
			tmp.update({node.name : [node.parent[0].name]})
		except:
			tmp.update({node.name : None})
	yaml_dict = {'parents' : tmp}
	yaml.dump(yaml_dict, file)

	# add children
	tmp = {}
	for node in graph:
		if len(node.children) == 0:
			tmp.update({node.name : None})
			continue
		children_names = [i.name for i in node.children]
		tmp.update({node.name : children_names})

	yaml_dict = {'children' : tmp}
	yaml.dump(yaml_dict, file)

	# add pseudo parents
	tmp = {}
	for node in graph:
		if len(node.p_parents) == 0:
			tmp.update({node.name : None})
			continue
		p_parents_names = [i.name for i in node.p_parents]
		tmp.update({node.name : p_parents_names})

	yaml_dict = {'p_parents' : tmp}
	yaml.dump(yaml_dict, file)

	# add potential values
	yaml_dict = {'potential_values' : list(range(1, len(graph[0].util)+1))}
	yaml.dump(yaml_dict, file)

	# add parent relations
	tmp = {}
	for node in graph:
		try:
			if node.parent[0] in node.agent_relation.keys():
				tmp.update({node.name : node.agent_relation.get(node.parent[0])})
			else:
				tmp.update({node.name : node.meeting_relation.get(node.parent[0])})
		except:
			tmp.update({node.name : None})

	yaml_dict = {'parent_relations' : tmp}
	yaml.dump(yaml_dict, file)
	
	# add pseudoparent relations
	tmp = {}
	for node in graph:
		if len(node.p_parents) == 0:
			tmp.update({node.name : None})
			continue
		tmp2 = {}
		for n in node.p_parents:
			if n in node.agent_relation.keys():
				tmp2.update({n.name : node.agent_relation.get(n)})
			else:
				tmp2.update({n.name : node.meeting_relation.get(n)})
		tmp.update({node.name : tmp2})
	yaml_dict = {'pseudo_parent_relations' : tmp}
	yaml.dump(yaml_dict, file)
	
	# add sep
	tmp = {}
	for node in graph:
		n = [i.name for i in node.p_parents]
		try:
			n.insert(0, node.parent[0].name)
		except:
			n.insert(0, None)
		tmp.update({node.name : n})
	yaml_dict = {'sep' : tmp}
	yaml.dump(yaml_dict, file)


	file.close()