import sqlite3
import config
import networkx as nx
from pyvis.network import Network

MainGraph = nx.MultiDiGraph()

con = sqlite3.connect(config.DBName)
cur = con.cursor()
cur.execute("SELECT * FROM users")
rows = cur.fetchall()
for row in rows:
    MainGraph.add_node(row[0],label='{}'.format(row[2]),title='{}'.format(row[4]))
    

cur.execute("SELECT * FROM follows")
rows = cur.fetchall()
for row in rows:
    MainGraph.add_edge(row[0],row[1])


cur.close()
con.close()

net = Network(directed=True,notebook=True,height="900px",width='1200px')
net.from_nx(MainGraph)
net.show("user_network.html")