# int, string, var, binop, neg, lneg, funcall, conv

from ssa import *

ntemp = 0
nbb = 0

bb = BasicBlock("B0")
bbs = [bb]
globals = []

def emit(op):
	bb.ops.append(op)

def newglobal(str):
	globals.append(str)
	return "global%i" % len(globals)

def new_bb():
	global nbb
	nbb += 1
	newbb = BasicBlock("B%i" % nbb)
	bbs.append(newbb)
	return newbb

def newtemp():
	global ntemp
	ntemp += 1
	return "%%t%i" % ntemp
	
def gen_op(op, res = None):
	if op[0] == "num":
		if res != None:
			emit(["=", res, op[1]])
		return op[1]
	elif op[0] == "str":
		glob = newglobal(op[1])
		if res == None:
			res = newtemp()
		emit(["load", res, glob])
		return res
	elif op[0] == "binop":
		if op[1] not in ["&&", "||"]:
			var1 = gen_op(op[2])
			var2 = gen_op(op[3])
			if res == None:
				res = newtemp()
			emit([op[1], res, var1, var2])
			return res
		elif op[1] == "&&":
			global nbb
			global bb
			newbb = new_bb()
			bb.br(newbb)
			bb = newbb
			if res == None:
				res = newtemp()
			gen_op(op[2], res)
			newbb = new_bb()
			final = new_bb()
			bb.brc(res, newbb, final)
			bb = newbb
			gen_op(op[3], res)
			bb.br(final)
			bb = final
			return res
	elif op[0] == "neg":
		var = gen_op(op[1])
		if res == None:
			res = newtemp()
		emit(["-", res, 0, var])
		return res
	elif op[0] == "funcall":
		temps = []
		for i in range(2, len(op)):
			temps.append(gen_op(op[i]))
		if res == None:
			res = newtemp()
		emit(["call", res, op[1], temps])
		return res
	elif op[0] == "var":
		if res != None:
			emit(["=", res, op[1]])
			return res
		return op[1]
	elif op[0] == "conv":
		return gen_op(op[2], res)

def gen_cmd(cmd):
	if cmd[0] == "while":
		global bb
		test = new_bb()
		bb.br(test)
		bb = test
		cond = gen_op(cmd[1])
		body = new_bb()
		final = new_bb()
		bb.brc(cond, body, final)
		bb = body
		for cmd in cmd[2]:
			gen_cmd(cmd)
		bb.br(test)
		bb = final
	elif cmd[0] == "attr":
		gen_op(cmd[2], cmd[1])
	elif cmd[0] == "return":
		bb.ret(gen_op(cmd[1]))

def gen_cmds(cmds):
	for cmd in cmds:
		gen_cmd(cmd)

gen_cmds([["attr", "a", \
   ["binop", "+", \
      ["binop", "*", \
         ["var", "a"], ["num", 5]],\
      ["binop", "+", \
         ["num", 3], ["var", "a"]]]],\
 ["while",\
  ["binop", "&&", \
      ["binop", ">", \
         ["var", "a"], ["num", 5]],\
      ["binop", "<=", \
         ["num", 3], ["var", "y"]]],[\
   ["while",["binop", ">", ["var", "a"], ["num", 5]],[\
   ["attr", "b", ["num", 3]], ["attr", "x", ["num", 3]]]], ["attr", "x", ["num", 3]]]],\
  ["return", ["var", "a"]]])

for b in bbs:
	print str(b)


