from ssa import *

def find_defs(blocks):
	defs = {}
	for b in blocks:
		for (var, body) in b.phis.items():
			defs[var] = b
		for i in range(len(b.ops)-1):
			op = b.ops[i]
			defs[op[1]] = b
	return defs

def is_dom(a, b):  # a dom b?
	if b.idom == a or b == a:
		return True
	elif b.idom == b:
		return False
	else:
		return is_dom (a, b.idom)

def find_loops(blocks):
	loops = []
	for b in blocks:
		for c in b.succs:
			if is_dom(c,b):
				inloop = [c, b]
				wl = [b]
				while len(wl) > 0:
					for p in wl.pop().preds:
						if is_dom(c,p) and p not in inloop:
							inloop.append(p)
							wl.append(p)
				loops.append((c, inloop))
	return loops

def can_move(v, defs, loop):
	return (not is_var(v)) or (defs[v] not in loop)

def licm(defs, loops):
	mudei = True
	while mudei:
		mudei = False
		for (header, nodes) in loops:
			pre_header = None

			for p in header.preds:
				if p not in nodes:
					pre_header = p
					break

			for n in nodes:
				i = 0
				while i < len(n.ops)-1:
					op = n.ops[i]
					if op[0] == "=":
						if can_move(op[2], defs, nodes):
							del n.ops[i]
							pre_header.ops.insert(-1, op)
							mudei = True
						else:
							i = i + 1
					else:
						if can_move(op[2], defs, nodes) and can_move(op[3], defs, nodes):
							del n.ops[i]
							pre_header.ops.insert(-1, op)
							mudei = True
						else:
							i = i + 1


