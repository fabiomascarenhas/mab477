from ssa import *
from sccp import *

b = []
for i in range(6):
    b.append(BasicBlock("B" + str(i)))

b[0]("""
  a = 3
  d = 2
     """)
b[0].br(b[1])

b[1]("""
  f = a + d
  g = 5
  a = g - d
  t = f <= g
     """)
b[1].brc("t", b[2], b[3])

b[2]("f = g + 1")
b[2].br(b[4])

b[3]("t = g >= a")
b[3].brc("t", b[5], b[4])

b[4]("d = 2")
b[4].br(b[1])

b[5].ret("f")

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

#rewrite(uses, values)

#for block in b:
#    if block.marked:
#        print str(block)
