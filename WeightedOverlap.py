import pandas as pd
import igraph as ig

# Load in the edgetable to be used
edgetable = pd.read_csv("TestNetwork.csv")

# Make a graph out of the edgetable
g = ig.Graph.TupleList(edgetable.itertuples(index=False), directed=False, weights=True)

# Get a list of all edge ids
total_edges = g.ecount()
EDGES = list(range(total_edges))
#print(EDGES)


##########################################################################################################
# Calculate weighted edge overlap
#
#	Ow = [Sum_nij_k=1(Wik + Wjk)]/(Si + Sj - 2Wij)
#
##########################################################################################################

print("Source,Target,WeightedOverlap")

for edge_id in EDGES:
	##### Get the i and j of the edge #####
	edge = g.es[edge_id]
	i =  g.vs[edge.source]["name"]
	j = g.vs[edge.target]["name"]

	##### Get the weight of the edge (wij) #####
	Wij = g.es[edge_id]["weight"]

	# print("Source:" + str(i) + ", Target:" + str(j) + ", Weight:" + str(Wij))

	##### Get the strength of node i (Si) #####
	node_name = i
	# print(node_name)
	# Find all edges connected to the node i
	incident_edge_ids = g.incident(node_name, mode="all")
	incident_edges = [g.es[edge_id] for edge_id in incident_edge_ids]
	# Set Si to 0, then add the weights to it
	Si = 0
	for edge in incident_edges:
		Si = Si + (edge["weight"])


	##### Get the strength of node j (Sj) #####
	node_name = j
	# print(node_name)
	# Find all edges connected to the node j
	incident_edge_ids = g.incident(node_name, mode="all")
	incident_edges = [g.es[edge_id] for edge_id in incident_edge_ids]
	# Set Sj to 0, then add the weights to it
	Sj = 0
	for edge in incident_edges:
		Sj = Sj + (edge["weight"])


	##### Get the neighbours of nodes i and j #####
	# Specify the two nodes to find shared neighbours for
	node1 = i
	node2 = j

	# Get the neighbours of both nodes
	neighbours1 = set(g.neighbors(node1))
	neighbours2 = set(g.neighbors(node2))

	# Find the common neighbours
	common_neighbours = neighbours1.intersection(neighbours2)

	# For all nodes in common neighbours, find the weights of nodes -> i, then add it to a value Wik
	# Set Wik to 0
	Wik = 0
	for neighbour in common_neighbours:
		i_neigh_edge = g.get_eid(i, neighbour, directed=False)
		i_neigh_weight = g.es[i_neigh_edge]["weight"]
		Wik = Wik + i_neigh_weight

	# For all nodes in common neighbours, find the weights of nodes -> j, then add it to a value Wjk
        # Set Wjk to 0
	Wjk = 0
	for neighbour in common_neighbours:
		j_neigh_edge = g.get_eid(j, neighbour, directed=False)
		j_neigh_weight = g.es[j_neigh_edge]["weight"]
		Wjk = Wjk + j_neigh_weight


	##### Calculate the edge overlap #####
	# Calculate the numerator
	numerator = Wik + Wjk

	# Calculate the denominator
	DoubleWij = Wij * 2
	denominator = Si + Sj - DoubleWij

	# Calculate weighted edge overlap
	Ow = numerator / denominator


	#print("Edge, i, j, Wij, Si, Sj, Wik, Wjk, Ow")
	#print(edge_id, i, j, Wij, Si, Sj, Wik, Wjk, Ow)

	print(str(i)+","+str(j)+","+str(Ow))
