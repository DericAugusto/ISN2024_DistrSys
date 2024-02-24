# 19/02/24 - TP Algorithmes distribuées et blockchain
# exercice 2, Q2 - page 3


import rpyc

conn = rpyc.connect("localhost",18861)
conn2 = rpyc.connect("localhost",18861)
conn3 = rpyc.connect("localhost",18861)


print("conn", conn.root.f())
print("conn2", conn2.root.f())
print("conn3", conn3.root.f())