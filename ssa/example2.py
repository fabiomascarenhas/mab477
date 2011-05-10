from ssa import *
from sccp import *

b = []
for i in range(13):
    b.append(BasicBlock("B" + str(i)))

b[0]("""
  i = 1
  j = 1
  k = 1
  l = 1
     """)
b[0].br(b[1])

b[1]("t0 = k < 10")
b[1].brc("t0", b[2], b[6])

b[2]("""
  j = i
  t1 = j > 2
     """)
b[2].brc("t1", b[3], b[4])

b[3]("l = 2")
b[3].br(b[5])

b[4]("l = 3")
b[4].br(b[5])

b[5]("k = k + 1")
b[5].br(b[7])

b[6]("k = k + 2")
b[6].br(b[7])

b[7]("y = i + j")
b[7]("z = k + l")
b[7].br(b[8])

b[8]("t2 = l < 50")
b[8].brc("t2", b[9], b[10])

b[9]("l = l + 4")
b[9].br(b[10])

b[10]("t3 = l < 10")
b[10].brc("t3", b[8], b[11])

b[11]("""
  i = i + 6
  t4 = i < 20
      """)
b[11].brc("t4", b[1], b[12])

b[12].ret("y")

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
