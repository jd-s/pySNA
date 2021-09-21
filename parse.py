#!/usr/bin/python3

from optparse import OptionParser
import os
from fnmatch import fnmatch
import networkx as nx
from bs4 import BeautifulSoup
import requests

parser = OptionParser()
parser.add_option("-i", "--input", dest="inputfolder",
                  help="Input folder", metavar="FILE")
parser.add_option("-o", "--output", dest="outputfile",
                  help="Output file", default="out.xml", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_true", dest="verbose", default=False,
                  help="don't print status messages to stdout")
parser.add_option("-s", "--onlysn",
                  action="store_true", dest="onlysna", default=False,
                  help="export only social network")
		  
parser.add_option("-b", "--ignorebook",
                  action="store_true", dest="ignorebook", default=False,
                  help="ignore biblical book in export")		  
		  

(options, args) = parser.parse_args()
pattern = "*.sna"

print (str(options.onlysna))
G=nx.Graph(selfloops=False)

def getix(url):
    document = {}
    try:
        #print (url)
        keywords = []
        page2 = requests.get(url, "lxml" )
        #print (page2.text)
        #if "Es ist ein Fehler aufgetreten" in page2.text:
        #    return None
        #if "An error has occurred" in page2.text:
        #    return None
        soup2 = BeautifulSoup(page2.text)
        trs = soup2.find_all('tr')
        # title
        tags = soup2.find_all('h3')
        for t in tags:
            if t.attrs['property'] == "name":
                document['title'] = t.text
        # other stuff
        for tr in soup2.find_all('tr'):
            for th in  tr.find('th'):
                #print ("..>"+th)
                if "Author" in th:
                    document['author'] = []
                    for td in tr.find('td'):
                        document['author'].append (td.text.strip())
                if "Published:" in th:
                    for td in tr.find('td'):
                        for span in tr.findAll('span', {"property":True}):
                            if "property" in span.attrs:
                                if span.attrs['property']=="location":
                                    document['location'] = span.text.strip()
                                if span.attrs['property']=="name":
                                    document['publisher-name'] = span.text.strip()
                                if span.attrs['property']=="datePublished":
                                    document['datePublished'] = span.text.strip()
        # Keyword
        for a in soup2.find_all('a', href=True):
            if a['href'].strip().endswith ('type=Subject'):
                keywords.append(a.text)
        document['keywords'] = keywords
    except Exception as e:
        if not options.verbose:
           print( "Exception in IXTheo:" +str(e))
    #print (str(document))
    return document

# Step 1: Create nodes

for path, subdirs, files in os.walk(options.inputfolder):
	for name in files:
		if fnmatch(name, pattern):
			if not options.verbose:
				print ("Processing "+os.path.join(path, name))
			mode = 0
			node_dict = {}
			#node_dict['Type'] = ""
			#node_dict['Name'] = ""
			#node_dict['Name_German'] = ""
			#node_dict['Groups'] = ""
			#node_dict['Sex'] = ""
			#node_dict['Background'] = ""
			#node_dict['Notes'] = ""
			#node_dict['Notes_German'] = ""
			#node_dict['Evidence'] = ""
			#node_dict['Type'] = ""
			#node_dict['Id'] = ""
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
						#	right = right.split(",")
						node_dict[left]=right
						#print (left+" -- "+right)
				if not options.verbose:
					print ("Added node "+node_dict['Name'])
				if options.onlysna:
					if not (node_dict['Type'] == "Person" or node_dict['Type'] == "Location" or node_dict['Type'] == "Church" or node_dict['Type'] == "Group"):
						continue
				G.add_node(node_dict['Name'])
				G.nodes[node_dict['Name']].update(node_dict)  
                        

# Step 2: Create edges

for path, subdirs, files in os.walk(options.inputfolder):
	for name in files:
		if fnmatch(name, pattern):
			if not options.verbose:
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
			#print (node_dict)
			if options.onlysna:
					if not (node_dict['Type'] == "Person" or node_dict['Type'] == "Location" or node_dict['Type'] == "Church" or node_dict['Type'] == "Group"):
						continue
			for line in connections:
				#rint (line)
				entry = line.split(";")
				if line.strip()[0]=="#":
					continue
				elif len(entry)<6:
					if not options.verbose:
						print (" Error in line '"+line+"' - not enough arguments!")
					continue
				else:
					edge_dict = {}
					#print (entry[0].upper())
					# Iterate Evidences
					
					# Need to check if we still need this...
					#edge_dict['Evidence'] = ""
					evidences = []
					if options.onlysna:
						# only sn
						edge_dict['Evidence'] = entry[4].strip()
					for ev in entry[4].strip().split(","):
						ev = ev.strip()
						# Check if bible ref
						if " " in ev:
							if ":" in ev.split(" ")[1]:
								if (not options.onlysna) and (not options.ignorebook) :
									edge_dict['Bible-Ref'] = ev
									book = ev.strip().split(" ")[0]
									if not book in G:
										# Add biblical book
										book_dict = {}
										book_dict['Name'] = book
										book_dict['Type'] = "BiblicalBook"
										G.add_node(book_dict['Name'])
										G.nodes[book_dict['Name']].update(book_dict)  
									evidences.append ( [book, {"reference": ev.strip(), "Bible-Ref": ev.strip(), "Relation": "hasReference"}] ) 
						# Check for other refs
						if "ixtheo" in ev:
							# if page
							page = ""
							if "#" in ev:
								page = ev.split("#")[1]
								ev = ev.split("#")[0]
							if not options.onlysna:
								document = getix(ev.strip())
								if 'title' in document:
									# document
									if not 'datePublished' in document:
											document['datePublished'] = "0"
									docidentifier = document['datePublished']+":"+document['title'].replace(" ", "_")[0:15]
									if docidentifier not in G:
										doc_dict = {}
										doc_dict['Name'] = docidentifier
										doc_dict['Type'] = "Literature" 
										doc_dict['Title'] = document['title']
										doc_dict['URI'] = ev.strip()
										doc_dict['datePublished'] = document['datePublished']
										G.add_node(doc_dict['Name'])
										G.nodes[doc_dict['Name']].update(doc_dict)  
									for author in document['author']:
										authid = author.replace(" ", "_")
										if not authid in G:
											auth_dict = {}
											auth_dict['Name'] = authid
											auth_dict['Type'] = "Author" 
											auth_dict['Fullname'] = author
											G.add_node(auth_dict['Name'])
											G.nodes[auth_dict['Name']].update(auth_dict)  
										G.add_edge (authid, docidentifier)
										G[authid][docidentifier]['Relation'] = "isAuthorOf"
									if page != "":
										evidences.append ( [docidentifier, {"reference": docidentifier, "page": page, "Relation": "hasReference"}] ) 
									else:
										evidences.append ( [docidentifier, {"reference": docidentifier, "Relation": "hasReference"}] ) 
								else:
									if not options.verbose:
										print ("No data found on IX")
					 
					edge_dict['Year'] = entry[5].strip()
					edge_dict['Relation'] = entry[6].strip()
					edge_dict['Strong'] = "weak"
					#edge_dict['Relation'] = ""
					if entry[1].upper().strip() == "GROUP" and entry[2].upper().strip() != "GROUP":
						print ("ERROR: Group at wrong position!")
					if entry[0].upper().strip() == "W":
						edge_dict['Strong'] = "weak"
					if entry[0].upper().strip() == "S":
						edge_dict['Strong'] = "strong"
					elif  entry[0].upper().strip() == "U":
						edge_dict['Strong'] = "unclear"
					elif  entry[0].upper().strip() == "A" or entry[0].upper().strip() == "N":
						edge_dict['Strong'] = "negative"
					# per Default all non-person edges are not strong
					if entry[1].upper().strip() != "PERSON" and entry[1].upper().strip() != "GROUP":
						edge_dict['Strong'] = "weak"
						#print ("-")
					#print (edge_dict['Strong'])
					if entry[2].strip().upper() == "GROUP":
						for (p, d) in G.nodes(data=True):
							#print (G[node])
							if "Groups" in d:
								if entry[3].strip() in d['Groups'].replace("'","").split(","):
									#print (node_dict['Name'] + "  "+ p)
									if node_dict['Name']!= p:
										G.add_edge (node_dict['Name'], p)
										for key, value in edge_dict.items():
											#print (str(key)+"  "+str(value))
											G[node_dict['Name']][p][str(key)] = value
											
										#G.edges[node_dict['Name']][p].update(edge_dict)
					else:
						if node_dict['Name'] != entry[3].strip():
							# Chekf for categories
							if entry[1].upper().strip() == "GREEK" or entry[1].upper().strip() == "HEBREW":
								if not options.onlysna:
									# Original Naming
									# Check if node exists
									if entry[3].strip() not in G:
										# Create Node
										node_dict2 = {}
										node_dict2['Name'] = entry[3].strip()
										node_dict2['Origin'] = entry[1].strip()
										node_dict2['Type'] = "Entity"
										G.add_node(node_dict2['Name'])
										G.nodes[node_dict2['Name']].update(node_dict2) 
									# Create Edge
									G.add_edge (node_dict['Name'], entry[3].strip())
									for key, value in edge_dict.items():
										G[node_dict['Name']][entry[3].strip()][str(key)]=value
									# Create Evidences
									for ev in evidences:
										G.add_edge (node_dict['Name'], ev[0])
										G.add_edge (entry[3].strip(), ev[0])
										for key, value in ev[1].items():
											G[node_dict['Name']][ev[0]][str(key)]=value
											G[entry[3].strip()][ev[0]][str(key)]=value
							else:
								# If target does not exist
								if entry[3].strip() not in G:
									continue
								G.add_edge (node_dict['Name'], entry[3].strip())
								for key, value in edge_dict.items():
									G[node_dict['Name']][entry[3].strip()][str(key)]=value
								# Create Evidences
								for ev in evidences:
									G.add_edge (node_dict['Name'], ev[0])
									G.add_edge (entry[3].strip(), ev[0])
									for key, value in ev[1].items():
										G[node_dict['Name']][ev[0]][str(key)]=value
										G[entry[3].strip()][ev[0]][str(key)]=value
								#G.edges[node_dict['Name']][ entry[3].strip()].update(edge_dict)
				
## ------------------------------------------------------------------------------
# w	;	Type	;	Group/E	;	Name	;	Evidence		;	Year	;	Note
## ------------------------------------------------------------------------------
#s	;	Person	;	Group	; 	Apostel	;					;			;

if options.outputfile.upper().endswith("GRAPHML"):
	nx.write_graphml(G,options.outputfile)
elif options.outputfile.upper().endswith("GEXF"):
	nx.write_gexf(G,options.outputfile)
else:
	print ("Error: Can't write specific format.")
