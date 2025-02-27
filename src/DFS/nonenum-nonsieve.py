# from pseudeo_clique_caller.py import enumPseudoClique_1st_level
import util
import copy
# import numpy as np
import sys
import time
import pickle
import profile
from collections import defaultdict

def f_cover(SS):
	# print "SS", SS
	if len(SS) == 0:
		return 0
	covered_v = set()
	for S in SS:
		covered_v |= S

	return len(covered_v)

def N(S, E, V): # N(x)={y in V(G)| (x,y) in E(G)}, N(S)=U x in S N(x);
	# print "S,V",S,V
	N_S = set()
	for u in S:
		for v in set(V):
			if(frozenset([u, v]) in E): # neighbors
				N_S.add(v)
	return N_S

def comp_Potential(K, V_remain, E, theta, x, N_r, Union, AdjList):
	N_x = set()
	for edge_weight in AdjList[x]:
		if(edge_weight[0] in Union): # neighbors
			N_x.add(edge_weight[0])
	# print len(N_x), len(N_x_new)

	# print "New",time.time()
	N_r_x = N_x & N_r

	######### possible opt??? Need to go over all vs ###########
	# N_x2 = set()
	# for v in set(N_r):
	# 	if(frozenset([x, v]) in E): # neighbors
	# 		N_x2.add(v)
	# print "N_r_x", N_r_x, "N_x2", N_x2
	deg_x_S = len(N_x & K)

	
	# print "N_r_S",N_r, "N_x",N_x, N_r_x
	potential = len(N_r_x) + len(N_r)*(deg_x_S - theta*(len(K) +1.0 ))
	return potential


def sort_N_r(K, V_remain, E, theta, N_r, AdjList):
	potential_D = {}
	global D
	start_time = time.time()
	Union = K | V_remain
	for x in N_r:
		# potential_D[x] = 1.0
		potential_D[x] = comp_Potential(K, V_remain, E, theta, x, N_r, Union, AdjList)
		# print "potential:",x,potential_D[x]
		# print "g_degree:",x,D[x]
	# print "Done potential", time.time() - start_time
	return sorted(N_r, key = lambda k: (potential_D[k], D[k]), reverse = True)


def compute_N_r_New(K, V_remain, E, theta, AdjList): # find all gamma neighbors on set S from V_remain
	# return set(V_remain)
	N_r = set()
	# print N_r

	# if (len(K) == 1):
	# 	u = K.pop()
	# 	for v in V_remain:
	# 		if(frozenset([u, v]) in E and E[frozenset([u, v])] >= theta):
	# 			N_r.add(v)

	# 	return N_r

	if (len(K) == 1):
		u = K.pop()
		for edge_weight in AdjList[u]:
			if edge_weight[1] >= theta:
				N_r.add(edge_weight[0])
		return N_r


	# base_density = util.computeDensity(K, E, isWeight)
	base_density = util.computeDensityNew(set(K), AdjList)
	n = len(K)
	edge_weight = base_density*(n-1)*n/2.0

	for v in V_remain:
		new_edge_weight = edge_weight
		for u in K:
			if(frozenset([u, v]) in E): # neighbors
				new_edge_weight+= E[frozenset([u, v])]
				# new_edge_weight+= 1

		new_density = new_edge_weight*2/((n+1)*n)
		if new_density >= theta:
			N_r.add(v)	

	return N_r	

def grasp_sort(K, V_remain, E, theta, AdjList): #''' bottleneck! '''

	# t0 = time.time()
	N_r = compute_N_r_New(K, V_remain, E, theta, AdjList)

	# print "time of gamma neighbors new", time.time() - t0, len(N_r)

	
	# t0 = time.time()

	# print "N_R here!!!!!!", len(N_r)
	# if len(N_r) > 0:
	# 	N_r_sorted = sort_N_r(K, V_remain, E, theta, N_r, AdjList) #''' bottleneck! '''
	# # print "time of N_r sort", time.time() - t0
	# 	return N_r_sorted
	# else:
	# 	return set()
	N_r_sorted = sort_N_r(K, V_remain, E, theta, N_r, AdjList) #''' bottleneck! '''
	return N_r_sorted


def enumPseudoClique(K, V_remain, E, V, AdjList, theta, max_dense, dense, Ancestors, CoveredV):
	''' --------------@para: no of elem in K-------------- '''
	global max_gain
	global first_branch
	leaf_node = 1
	
	# for elem in K:
	# 	print str(elem) + "\t",
	# print float(dense)
	# print
	# if len(K) > min_elem_output:
	# print dense,
	# print "\t" + str(K)
	# print "first_branch", first_branch
	# print "V_remain:", len(V_remain)
	if 0 == len(V_remain):
		# print "===========reach base case ==========="
		# print float(dense), K

		first_branch = False
		K_set = set(K)
		CoveredV |= K_set
		# all_first_branch.append(K_set)

		should_add = True
		for each_set in max_dense:
			if set(each_set[0]).issuperset(set(K)):
				# print "Here"
				should_add = False
				break
		if should_add:
			# print "leaf node", K, "dense", dense 
			max_dense.append((K, dense))
		 	return


	if len(K) != 0: # 1st level
		# print "grasp_sort start"
		# time_start = time.time()
		V_remain_in_seq = grasp_sort(set(K), set(V_remain), E, theta, AdjList)
		# print "grasp_sort end", time.time() - time_start
	
	# print "V_remain_in_seq", len(V_remain_in_seq)
	if len(K) == 1 and len(V_remain_in_seq) == 0:
		# print "returned"
		return
	for i in range(len(V_remain_in_seq)):
		# print "i", i
		v = V_remain_in_seq[i]

		K_new = copy.copy(K)
		# V_new = V_remain_in_seq[i+1:]
		# Ancestors = set(K_new) | set(V_remain_in_seq[:i])
		# print K,"sibling here ",V_remain_in_seq[:i]
		# print "V_remain_in_seq",V_remain_in_seq, " i",i
		
		# check connectivity, if v is not connect to K_new, pick another v
		v_deg = 0
		for u in K_new:
			# if v in AdjList[u]:
			if frozenset((u,v)) in E:
				# break
				v_deg+=1
		if K_new != [] and v_deg == 0:
			# print "pick another v"
			continue # pick another v
		# end	

		# D = util.computeDegree(list(K_new), E)
		# print "D",D,"K_new",K_new
		# min_deg = util.min_degree(D)

		K_new.append(v)

 		# print "K_new",K_new
 		start_time = time.time()
		# new_dense = util.computeDensity(set(K_new), E, isWeight)
		# print "dense compute time", time.time() - start_time, new_dense

		# start_time = time.time()
		new_dense = util.computeDensityNew(set(K_new), AdjList)
		# print "new d", new_dense
		# print "new dense compute time", time.time() - start_time, new_dense

		if new_dense >= theta:
			# print "Old Ancestors:", Ancestors
			if(not first_branch):
				# print "tracing back... "
				# continue
				return
			# print "v is", v
 			# print "Ancestors:", Ancestors_new
	 		if v in Ancestors:
	 			# print "In Ancestors......."
 				continue

			V_new = list(N(set(K_new), E, V)  - set(K_new) - Ancestors)
			Ancestors_new =  Ancestors | set(V_remain_in_seq[:i])

			# if (first_branch or sieve_nonleaf(set(K_new), K_new)):
			# if(first_branch):
			# if(True):

			leaf_node = 0
			# print "Next level"
			enumPseudoClique(K_new, V_new, E, V, AdjList, theta, max_dense, new_dense, Ancestors_new, CoveredV)

		# else:
		# 		print "stop enumerate due to dense"


	# print "leaf_node", leaf_node, set(K)
	if leaf_node:
		# print "leaf_node"
		# print float(dense), K

		K_set = set(K)
		CoveredV |= K_set
		# all_first_branch.append(K_set)
		should_add = True
		for each_set in max_dense:
			if set(each_set[0]).issuperset(set(K)):
				# print "Here"
				should_add = False
				break
		if should_add:
			# print "leaf node", K, "dense", dense 
			max_dense.append((K, dense))
	
	first_branch = False			
	# print "Reset Ancestors......"
	Ancestors = set()
	# print "S len:"
	# for i in range(k, k*m + 1, 1):
	# 	print len(S[i]),
	# print
	

def mergeOnce(V, E, AdjList, D, MdsList, merge_perc):
	newMdsHashSet = set()
	newMdsList = []
	global theta
	# fout = open("./result/extendOptMerge0.5Overlap.txt",'w+')
	fout = open("./merge_result/"+input_file.split("/")[-1].split(".")[0] + "-d" + str(theta)+ "-merge" + str(merge_perc) + ".txt",'w+')

	cnt = 0
	for mds in MdsList:
		# print mds
		if len(mds[0]) > 2: 
			cnt+=1 

	print "In merge. # Mds (>3)", cnt

	l = MdsList
	while len(l) >0:
		# print "len l", len(l)		
		first, rest = l[0][0], l[1:]
		# print "first", first
		first = set(first)

		lf = -1
		while len(first)>lf:
			lf = len(first)

			rest2 = []

			for (r,w) in rest:
				
				if len(first & set(r))*1.0/len(first) > merge_perc:
					first |= set(r)
					print "merging"
				else:
					rest2.append((r,w))
			rest = rest2
		newMdsList.append(first)
		# print rest2
		l = rest
	
	cnt = 0
	for mds in newMdsList:
		if len(mds) > 2: cnt+=1 
	print "Done merge. # Mds (>3)", cnt
	
	coverSet = set()
	for mds in newMdsList:
		if len(mds) < 3:
			# print "Too small",mdsObj.vs
			continue
		for v in mds:
			coverSet.add(v)				
			fout.write(v + '\t')
		fout.write('\n')
	
	print "Merge Cover:",len(coverSet)
	# check_overlap(newMdsList)
	# for elem in newMdsHashSet:
	# 	print elem	

def doMerge(aggregated_max_dense):
	aggregated_max_dense_merged = set()
	MdsList = list(aggregated_max_dense)
	overlapScore = {}
	overlapG_V = range(0,len(MdsList))
	overlapG_Adj = {}
	for i in range(0,len(MdsList)-1):
		for j in range(i+1,len(MdsList)):
			a = MdsList[i]
			b = MdsList[j]
			newSet = a&b
			# print "newSet", newSet
			curScore = float(len(newSet)**2)/(len(a)*len(b))
			overlapScore[frozenset((a, b))] = curScore
			if curScore > 0.5:			
				# print i,j,"score",curScore
				if i not in overlapG_Adj:
					overlapG_Adj[i] = []

				overlapG_Adj[i].append(j)

				if j not in overlapG_Adj:
					overlapG_Adj[j] = []
					
				overlapG_Adj[j].append(i)
			# print i,j
	# print len(overlapScore), len(overlapG_Adj)
	print overlapG_Adj.keys()
	connectedGroups = bfs(overlapG_V, overlapG_Adj)
	print "connectedGroups"
	for elem in connectedGroups:
		# print "New....."
		if len(elem)>1:
			# print "Old"
			newMds = frozenset()
			for i in elem:
				newMds |= MdsList[i]
				# print MdsList[i],
			aggregated_max_dense_merged.add(newMds)
			# print
			# print "New", newMds
		else:
			# print "Old", MdsList[elem[0]]
			aggregated_max_dense_merged.add(MdsList[elem[0]])

	return aggregated_max_dense_merged
	# for elem in overlapScore:
	# 	if
	# 	print elem, overlapScore[elem]

# main
def main(input_file):
	
	global D
	start_time = time.time()
	(V, E, AdjList, D) = util.readinputNumpy(input_file, mytype = "str", myDelimiter = "\t")
	# print "time in reading", time.time() - start_time
	max_dense = []
	# time.sleep(0.5)
	
	global first_branch
	# D = util.computeDegree_dict(list(V),E)
	# print "D computed"

	CoveredV = set()
	Ancestors = set()
	# print "start looping... "
	for i in range(len(V)):
		# print "V[i]",V[i]
		curV = V[i]

		first_branch = True

		# if all_full:
			# continue

		# print "CoveredV", (curV in CoveredV), curV

		if (curV in CoveredV):
			# print "***********Skip seed ***********: ", i
			continue

		K = [V[i]]
		V_new = copy.copy(V)
		V_new.pop(i)
		print "========= progress =========: ", i, len(V)
		# print "Ancestors:", set(V[:i])
		# print "S keys",len(S.keys())
		enumPseudoClique(K, V_new, E, V, AdjList, theta, max_dense, 1.0, Ancestors, CoveredV)
		Ancestors.add(curV)

	print "MDS time", time.time() - start_time
	# mergeOnce(V, E, AdjList, D, max_dense, merge_perc = .8)
	# print "Merge time", time.time() - start_time
	# return
	fout = open("./result/" +input_file.split("/")[-1].split(".")[0] +"-d" +str(theta) + ".txt", "w+")
	realSize = 0
	coverage_set = set()
	for each_set in max_dense:
		if(len(each_set[0]) > 2):
			realSize+=1

			for node in each_set[0]:
				coverage_set.add(node)
				fout.write(str(node) + "\t")
			fout.write("\n")
			# for elem in each_set[0]:
			# 	# if elem not in coverage_set:
			# 		# print elem
			# print str(each_set[0]) + '\t' + str(each_set[1])

	print "coverage: ",len(coverage_set)
	# print "====="
	# print "Best v",maxV, "with coverage",maxF


	# print "========================="
	# print "All first_branch. threshold", theta
	# print "========================="
	# fout = open("./result/" +input_file.split("/")[-1].split(".")[0] +"-d" +str(theta) + ".txt", "w+")
	# coverage_set = set()
	# realSize = 0
	# for elem in all_first_branch:
	# 	if(len(elem) >= min_elem_output):
	# 		# if frozenset(elem) in coverage_set:
	# 			# print "subset"
	# 			# continue
			
	# 		# coverage_set.add(frozenset(elem))
	# 		# density = util.computeDensityNew(elem, AdjList)
	# 		# print density
	# 		realSize+=1
	# 		for node in elem:
	# 			fout.write(str(node) + "\t")
	# 		fout.write("\n")
	# 		# 	print str(node) + "\t",
	# 		# print
	# print "total MDS ", len(all_first_branch), "with size >=", min_elem_output, ":",realSize
	# print "total MDS ", len(max_dense), "with size >=", min_elem_output, ":",realSize

		# if(len(elem[0]) >= 3 and len(elem[0]) <=8 ):



theta = 0.0
if(len(sys.argv) != 5):
	print "Usage: **.py <inputfile> <k> <threshold> <min_elem_output>"
	# input_line  = raw_input("Exit? Y or N: ")
	# if(input_line in ['Y','y','Yes','YES','yes']):
	# 	sys.exit()
	# print "Running default... k=20, theta=0.97, min_elem_output=3"

	
	theta = 0.6
	min_elem_output = 3
	print "Running default... theta=",theta,"min_elem_output=",min_elem_output
	

else:
	# input_file = sys.argv[1]
	theta = float(sys.argv[3])
	min_elem_output = int(sys.argv[4])

# m = 10

D = {}
# covers = set()
first_branch = True
all_first_branch = []


# profile.run('main(input_file)')
input_file_list = [
"../../data/data_bio/cl1_datasets/datasets/gavin2006_socioaffinities_rescaled.txt",
"../../data/data_bio/cl1_datasets/datasets/collins2007.txt",
"../../data/data_bio/cl1_datasets/datasets/krogan2006_core.txt",
"../../data/data_bio/cl1_datasets/datasets/krogan2006_extended.txt",
]
input_file = input_file_list[0]

# for theta in [0.9, 0.8, 0.7, 0.6]:
for i in [0]:

	input_file = input_file_list[i]
	theta = 0.8
# for theta in [0.6, 0.5, 0.4, 0.3]:
# for input_file in input_file_list:
	start_time = time.time()
	fout = input_file.split("/")[-1].split(".")[0]
	# print fout
	print "Reading from:", input_file
	print "theta",theta
	# fout = open("./result/" +input_file.split("/")[-1].split(".")[0] + "_mds.txt", "w+")

	main(input_file)
	print("%s seconds" % round((time.time() - start_time), 2))
	print
	break








