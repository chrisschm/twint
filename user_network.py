import sqlite3
import config
import networkx as nx
from pyvis.network import Network

LIMIT_TO_SHOW = 500

MainGraph = nx.MultiGraph()

con = sqlite3.connect(config.DBName)
cur = con.cursor()
sql = "SELECT * FROM users WHERE id IN (SELECT id FROM follows GROUP BY id ORDER BY COUNT(follower) DESC LIMIT {})".format(LIMIT_TO_SHOW)
cur.execute(sql)
rows = cur.fetchall()
for row in rows:
    MainGraph.add_node(row[0],label='{}'.format(row[2]),title='{}'.format(row[4]))    

sql = "SELECT * from follows WHERE id IN (SELECT id FROM follows GROUP BY id ORDER BY COUNT(follower) DESC LIMIT 500) \
        AND follower IN (SELECT follower FROM follows GROUP BY id ORDER BY COUNT(follower) DESC LIMIT {})".format(LIMIT_TO_SHOW)
cur.execute(sql)
rows = cur.fetchall()
for row in rows:
    MainGraph.add_edge(row[0],row[1])

cur.close()
con.close()

net = Network(directed=False,notebook=True,height="900px",width='1200px')
net.from_nx(MainGraph)
net.show("user_network.html")