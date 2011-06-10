from ssa import *
from const import *
from dvnt import *

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
  x = b + a
  t = a <= d
     """)
b[5].brc("t", b[6], b[8])

b[6]("d = 6")
b[6].br(b[7])

b[7]("b = a + b")
b[7].br(b[3])

b[8]("c = 8")
b[8].br(b[7])

print_cfg(b)

full_ssa(b)

print "\nSSA:\n====\n"

print_cfg(b)

full_dvnt(b[0])

print "\nGVN:\n====\n"

print_cfg(b)

full_sccp(b)

print_cfg(b)

