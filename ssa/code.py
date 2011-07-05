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
		emit(["loadi", res, glob])
		return res
	elif op[0] == "[i]":
		base = gen_op(op[1])
		off = newtemp()
		gen_op(op[2], off)
		emit(["*", off, off, 4])
		emit(["+", off, off, base])
		if res == None:
			res = newtemp()
			emit(["loadi", res, off])
		return res
	elif op[0] == "[c]":
		base = gen_op(op[1])
		off = newtemp()
		gen_op(op[2], off)
		emit(["+", off, off, base])
		if res == None:
			res = newtemp()
			emit(["loadc", res, off])
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

ast = [[ 'func', 'atoi', [ 's_0x100100150', ],],\
[ 'func', 'printf', [ 's_0x100100240', '...', ],],\
[ 'func', 'main', [],\
[  [ 'attr', 'x_0x100100510', [ 'num', 0 ]],   [ 'attr', 'n_0x1001004d0', [ 'num', 1 ]],   [ 'attr', 'a_0x100100690', [ 'num', 0 ]],   [ 'while', [ 'binop', '<', [ 'var', 'a_0x100100690'], [ 'var', 'n_0x1001004d0']],   [    [ 'attr', 'b_0x100100650', [ 'num', 0 ]],     [ 'while', [ 'binop', '<', [ 'var', 'b_0x100100650'], [ 'var', 'n_0x1001004d0']],     [      [ 'attr', 'c_0x100100610', [ 'num', 0 ]],       [ 'while', [ 'binop', '<', [ 'var', 'c_0x100100610'], [ 'var', 'n_0x1001004d0']],       [        [ 'attr', 'd_0x1001005d0', [ 'num', 0 ]],         [ 'while', [ 'binop', '<', [ 'var', 'd_0x1001005d0'], [ 'var', 'n_0x1001004d0']],         [          [ 'attr', 'e_0x100100590', [ 'num', 0 ]],           [ 'while', [ 'binop', '<', [ 'var', 'e_0x100100590'], [ 'var', 'n_0x1001004d0']],           [            [ 'attr', 'f_0x100100550', [ 'num', 0 ]],             [ 'while', [ 'binop', '<', [ 'var', 'f_0x100100550'], [ 'var', 'n_0x1001004d0']],             [              [ 'attr', 'x_0x100100510', [ 'binop', '+', [ 'var', 'x_0x100100510'], [ 'num', 1 ]]],               [ 'attr', 'f_0x100100550', [ 'binop', '+', [ 'var', 'f_0x100100550'], [ 'num', 1 ]]], ]],             [ 'attr', 'e_0x100100590', [ 'binop', '+', [ 'var', 'e_0x100100590'], [ 'num', 1 ]]], ]],           [ 'attr', 'd_0x1001005d0', [ 'binop', '+', [ 'var', 'd_0x1001005d0'], [ 'num', 1 ]]], ]],         [ 'attr', 'c_0x100100610', [ 'binop', '+', [ 'var', 'c_0x100100610'], [ 'num', 1 ]]], ]],       [ 'attr', 'b_0x100100650', [ 'binop', '+', [ 'var', 'b_0x100100650'], [ 'num', 1 ]]], ]],     [ 'attr', 'a_0x100100690', [ 'binop', '+', [ 'var', 'a_0x100100690'], [ 'num', 1 ]]], ]],   [ 'call', 'printf', [[ 'str',"%d\n"], [ 'var', 'x_0x100100510'], ]],   [ 'return', [ 'num', 0 ]], ]],\
]

#gen_cmds([["attr", "a", \
#   ["binop", "+", \
#      ["binop", "*", \
#         ["var", "a"], ["num", 5]],\
#      ["binop", "+", \
#         ["num", 3], ["var", "a"]]]],\
# ["while",\
#  ["binop", "&&", \
#      ["binop", ">", \
#         ["var", "a"], ["num", 5]],\
#      ["binop", "<=", \
#         ["num", 3], ["var", "y"]]],[\
#   ["while",["binop", ">", ["var", "a"], ["num", 5]],[\
#   ["attr", "b", ["num", 3]], ["attr", "x", ["num", 3]]]], ["attr", "x", ["num", 3]]]],\
#  ["return", ["var", "a"]]])

gen_cmds(ast[2][3])

for b in bbs:
	print str(b)


