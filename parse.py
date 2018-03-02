#!/usr/bin/python3

from optparse import OptionParser
import os
from fnmatch import fnmatch
import networkx as nx

parser = OptionParser()
parser.add_option("-i", "--input", dest="inputfolder",
                  help="Input folder", metavar="FILE")
parser.add_option("-o", "--output", dest="outputfile",
                  help="Output file", default="out.xml", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()
pattern = "*.sna"

G=nx.Graph(selfloops=False)


# Step 1: Create nodes

for path, subdirs, files in os.walk(options.inputfolder):
	for name in files:
		if fnmatch(name, pattern):
			print ("Processing "+os.path.join(path, name))
			mode = 0
			node_dict = {}
			with open(os.path.join(path, name)) as fp:
				for cnt, line in enumerate(fp):
					if line.strip() == "":
						continue
					elif line.strip()[0] == "#":
						continue
					elif line.strip() == "BEGIN EDGES":
						mode = 1;
						break
					elif ":" in line:
						values = line.strip().split(":", 1)
						left = values[0].strip().lower()
						# Uppercase convention
						left = list(left)
						left[0]=left[0].upper()
						left= "".join(left)
						right = values[1].strip().strip("'").strip()
						if left.upper() == "GROUPS":
							right.replace(' ', '')
						# Does not work, since GML cannot export lists sadly
						#	right = right.split(":")
						node_dict[left]=right
						#print (left+" -- "+right)
				G.add_node(node_dict['Name'])
				G.nodes[node_dict['Name']].update(node_dict)  

# Step 2: Create edges

for path, subdirs, files in os.walk(options.inputfolder):
	for name in files:
		if fnmatch(name, pattern):
			print ("Processing Edges for "+os.path.join(path, name))
			mode = 0
			node_dict = {}
			connections = []
			with open(os.path.join(path, name)) as fp:
				for cnt, line in enumerate(fp):
					if line.strip() == "":
						continue
					elif line.strip()[0] == "#":
						continue
					elif (":" in line) and (mode == 0):
						values = line.strip().split(":", 1)
						left = values[0].strip().lower()
						# Uppercase convention
						left = list(left)
						left[0]=left[0].upper()
						left= "".join(left)
						right = values[1].strip().strip("'").strip()
						if left.upper() == "GROUPS":
							right.replace(' ', '')
						# Does not work, since GML cannot export lists sadly
						#	right = right.split(":")
						node_dict[left]=right
						#print (left+" -- "+right)
					elif mode == 1:
						if "INCLUDE" in line:
							filename = line.split(" ")[1].strip()+".sng"
							with open(os.path.join(path, filename)) as fp2:
								for cnt2, line2 in enumerate(fp2):
									connections.append (line2.strip())
						elif line.strip == "":
							continue
						else:
							if line.strip()[0] == "#":
								continue
							else:
								connections.append (line.strip())
					elif line.strip() == "BEGIN EDGES":
						mode = 1
						continue
				#G.add_node(node_dict['name'])
				#G.nodes[node_dict['name']].update(node_dict)  
			for line in connections:
				#rint (line)
				entry = line.split(";")
				if line.strip()[0]=="#":
					continue
				elif len(entry)<6:
					print (" Error in line '"+line+"' - not enough arguments!")
					continue
				else:
					edge_dict = {}
					#print (entry[0].upper())
					edge_dict['Evidence'] = entry[4].strip()
					edge_dict['Year'] = entry[5].strip()
					edge_dict['Note'] = entry[6].strip()
					edge_dict['Strong'] = True
					if entry[0].upper().strip() == "W":
						edge_dict['Strong'] = False
					if entry[1].upper().strip() != "PERSON":
						edge_dict['Strong'] = False
						#print ("-")
					#print (edge_dict['Strong'])
					if entry[2].strip().upper() == "GROUP":
						for (p, d) in G.nodes(data=True):
							#print (G[node])
							if "Groups" in d:
								if entry[3].strip() in d['Groups'].split(":"):
									#print (node_dict['Name'] + "  "+ p)
									if node_dict['Name']!= p:
										G.add_edge (node_dict['Name'], p)
										for key, value in edge_dict.items():
											#print (str(key)+"  "+str(value))
											G[node_dict['Name']][p][str(key)] = value
											
										#G.edges[node_dict['Name']][p].update(edge_dict)
					else:
						if node_dict['Name'] != entry[3].strip():
							G.add_edge (node_dict['Name'], entry[3].strip())
							for key, value in edge_dict.items():
								G[node_dict['Name']][entry[3].strip()][str(key)]=value
							#G.edges[node_dict['Name']][ entry[3].strip()].update(edge_dict)
				
## ------------------------------------------------------------------------------
# w	;	Type	;	Group/E	;	Name	;	Evidence		;	Year	;	Note
## ------------------------------------------------------------------------------
#s	;	Person	;	Group	; 	Apostel	;					;			;


nx.write_graphml(G,options.outputfile)
