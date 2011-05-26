from ssa import *
from const import *

b = []
for i in range(7):
    b.append(BasicBlock("B" + str(i)))

b[0]("""
   b = 2
   i = 1
     """)
b[0].br(b[1])

b[1]("t = i > 100")
b[1].brc("t", b[6], b[2])

b[2]("""
   a = b + 1
   c = 2
   t = i % 2
   t = t == 0
     """)
b[2].brc("t", b[3], b[4])

b[3]("""
   d = a + d
   e = 1 + d
     """)
b[3].br(b[5])

b[4]("""
   d = 0 - c
   f = 1 + a
     """)
b[4].br(b[5])

b[5]("""
   i = i + 1
   t = a < 2
     """)
b[5].brc("t", b[6], b[1])

b[6].ret("0")

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

(vars, defs, uses) = def_uses(b)

print vars

values1 = sscp(vars, defs, uses)
values2 = sccp(b, vars, uses)

keys = values1.keys()
keys.sort()

for var in keys:
  print var, "\t", values1[var], "\t", values2[var]

rewrite(uses, values2)

for block in b:
    if block.live:
        print str(block)

