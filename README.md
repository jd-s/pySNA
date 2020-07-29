# pySNA
A simple Python Parser to convert Social Networks into a NetworkX graph and export it to Cytoscape, Gephi, etc.

This package can be used as a standalone command-line application.

<b>Content</b>
1. [ Features](#features)
2. [ Usage](#usage)
3. [ File Format](#file-format)
4. [ Further information ](#further-information)

# Features

pySNA parses sna-files (see [ File Format](#file-format)) and outputs a network file in graphml format. 

* sna-files are easy, human readable and very flexible. They can be used for a collaborative work on a social network.
* You can organize your work in subfolders and with generic input files. 
* The output format is an open format that can be used with many other applications like Cytoscape and Gephi. Currently, pySNA export gexf or graphml files (depending on the file extension). 

We propose a workflow that imports the output in Gephi. 

# Usage

After creating your files, you can execute pySNA as follows:

```
./parse.py -i /home/.../inputfolder -o /home/.../outputfolder/output.xml
```

The command parse has only two parameters: <code>-i</code> or <code>--input</code>  for the input folder. This folder and all subfolders will be parsed. <code>-o</code> or <code>--output</code> refers to the graphml output file. <code>-v</code> runs in quiet mode. If you only need a social network, use <code>-s</code>.

The parameter <code>-q</code> will run in quiet mode.

# File Format

The file format of sna-files is quiet easy. The first part of a file consists of an arbitrary list of meta data:

```
Type	 	: Person
Name 		: ’ Simon Petrus ’
Groups 		: ’ Apostel ’
Sex 		: male
Background 	: Hebrew
Notes 		: ’’
Evidence 	: ’’
```

Type can be freely set, name is the mandatory name of a node. Every node can be assigned to a set of groups. This makes it easier to add edges to all nodes in a group. All other values in the example are not mandatory. Feel free to add more or less information to your nodes. 

The second part of a sna-file begins with <code>BEGIN EDGES</code>:

```
BEGIN EDGES
INCLUDE apostel
s	;	Person	;	;	Johannes			;	Apg 3	;	;
w	;	Church	;	;	Samarien_Church			;	Apg 8	;	;
```

You can include sng-files which consist of edges. This makes it easier to make changes to all nodes in a group. For example, here every apostle includes the file apostel.sng - adding edges for all apostles can thus be done by only changing one single file. 

The next lines contain one edge each in a semicolon-separated way. The format is 
```
w;	Type;	Group/E	;	Name;	Evidence;	Year;	Relation
```
The first columns indicated, if it is a weak (w) or strong (s) tie. Type refers to the destination type. If we want to link to all nodes in a group, we can add <code>group</code> to the third column and add the groups name instead a nodes name to the fourth column. We can also add evidence, year and the type of relation (isMariedTo, isA, ...) to an edge.

Evidences can be split using a colon. You can refer to IXTheo entries (e.g. https://ixtheo.de/Record/109268283X). If you want to reference a particular page, use <code>https://ixtheo.de/Record/109268283X#120</code>.

# Further information

pySNA is licensed under the GNU General Public License v3.0.

If you use this software, please cite the following publication: J. Dörpinghaus, C. Stenschke. Ein kollaborativer Workflow zur historischen Netzwerkanalyse mit Open Source Software. FrOSCon 2018. In press: Science Track FrOSCon 2018.
