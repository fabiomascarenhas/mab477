from ssa import *
from sccp import *

b = []
for i in range(9):
    b.append(BasicBlock("B" + str(i)))

b[0]("""
  a = 0
  b = 0
  c = 0
  d = 0
  i = 1
     """)
b[0].br(b[1])

b[1]("""
  a = 5
  c = 3
  t = a < c
     """)
b[1].brc("t", b[2], b[5])

b[2]("""
  b = 2
  c = 3
  d = 4
     """)
b[2].br(b[3])

b[3]("""
  y = a + b
  z = c + d
  i = i + 1
  t = i <= 100
     """)
b[3].brc("t", b[1], b[4])

b[4].ret(0)

b[5]("""
  a = 5
  d = 3
  t = a <= d
     """)
b[5].brc("t", b[6], b[8])

b[6]("d = 6")
b[6].br(b[7])

b[7]("b = 7")
b[7].br(b[3])

b[8]("c = 8")
b[8].br(b[7])

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
