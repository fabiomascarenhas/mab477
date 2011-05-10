from ssa import *
from sccp import *

b = []
for i in range(8):
    b.append(BasicBlock("B" + str(i)))

b[0]("n = 5")
b[0].br(b[1])

b[1]("""
   k = 0
   i = 1
   j = 2
     """)
b[1].br(b[2])

b[2]("t = i <= n")
b[2].brc("t", b[3], b[4])

b[3]("""
   j = j * 2
   k = 1
   i = i + 1
     """)
b[3].br(b[2])

b[4].brc("k", b[5], b[6])

b[5]("r = j")
b[5].br(b[7])

b[6]("""
   i = i + 1
   r = i
     """)
b[6].br(b[7])

b[7].ret("r")

for block in b:
    print str(block)

dom_tree(b)

print

for block in b:
    print block.name + ":",
    for child in block.children:
        print " %s(%s)" % (child.name, child.idom.name),
    print

dom_frontier(b)

print

for block in b:
    print block.name + ":",
    for f in block.df:
        print " %s" % f.name,
    print

globals, blocks = find_globals(b)

print

print repr(globals)

print

add_phis(globals, blocks)

for block in b:
    print str(block)

print

ssa_rename(b)

for block in b:
    print str(block)

#values = sccp(b, uses)

#for var in values:
#    print var, values[var]
