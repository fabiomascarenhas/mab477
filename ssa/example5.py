from ssa import *
from const import *
from licm import *

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

defs = find_defs(b)
#for (var, block) in defs.items():
#	print var
#	print str(block)

loops = find_loops(b)
for (h, bs) in loops:
	print h.name + ": ",
	for block in bs:
		print block.name + ", ",
	print

licm(defs, loops)

for block in b:
    print str(block)

