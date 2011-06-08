from ssa import *

def fold(op):
    if not is_var(op[2]) and not is_var(op[3]):
        val = eval(str(op[2]) + op[0] + str(op[3]))
        if type(val) == bool:
            if val:
                val = 1
            else:
                val = 0
        op[0] = "="
        op[2] = val
        del op[3]
        return True
    else:
        return False

def lvn(b):
    c = 0
    vn = {}
    vn_var = {}
    for i in range(len(b.ops)-1):
        op = b.ops[i]
        if op[0] == "=":
            if op[2] not in vn:
                vn[op[2]] = c
                c += 1
            vn[op[1]] = vn[op[2]]
            vn_var[vn[op[2]]] = op[1]
        else: # op[1] = op[2] op[0] op[3]
            if fold(op): continue
            if op[2] not in vn:
                vn[op[2]] = c
                c += 1
            if op[3] not in vn:
                vn[op[3]] = c
                c += 1
            if op[0] == "+" or op[0] == "*":
                ops = [vn[op[2]], vn[op[3]]]
                ops.sort()
                sop = str(ops[0]) + op[0] + str(ops[1])
            else:
                sop = str(vn[op[2]]) + op[0] + str(vn[op[3]])
            if sop not in vn:
                vn[sop] = c
                c += 1
                vn[op[1]] = vn[sop]
                vn_var[vn[sop]] = op[1]
            else:
                vn[op[1]] = vn[sop]
                op[0] = "="
                op[2] = vn_var[vn[sop]]
                del op[3]

def lvn_blocks(bs):
    for b in bs:
        lvn(b)

def dvnt(b, vn):
    for (var, phi) in b.phis.items():
        (v1, b1) = phi[0]
        vn1 = vn.get(v1, v1)
        (v2, b2) = phi[1]
        vn2 = vn.get(v2, v2)
        useless = (vn1 == vn2)
        if useless:
            vn[var] = vn1
            del b.phis[var]
        else:   # phi(x2, x1) === "x1|x2"
            vns = [vn1, vn2]
            vns.sort()
            key = "|".join(vns)
            if key in vn:
                vn[var] = vn[key]
                del b.phis[var]
            else:
                vn[key] = var
    i = 0
    while i < len(b.ops)-1:
        op = b.ops[i]
        if op[0] == "=":
            vn[op[1]] = vn.get(op[2], op[2])
            del b.ops[i]
        else:
            op[2] = vn.get(op[2], op[2])
            op[3] = vn.get(op[3], op[3])
            if fold(op): continue
            if op[0] == "+" or op[0] == "*":
                ops = [op[2], op[3]]
                ops.sort()
                sop = str(ops[0]) + op[0] + str(ops[1])
            else:
                sop = str(op[2]) + op[0] + str(op[3])
            if sop in vn:
                vn[op[1]] = vn[sop]
                del b.ops[i]
            else:
                vn[sop] = op[1]
                i += 1
    branch = b.ops[-1]
    if branch[0] == "brc":
        branch[1] = vn.get(branch[1], branch[1])
        if not is_var(branch[1]):
            branch[0] = "br"
            if branch[1]:
                branch[1] = branch[2]
            else:
                branch[1] = branch[3]
            del branch[2]
            del branch[2]
    for succ in b.succs:
        for (var, pairs) in succ.phis.items():
            for pair in pairs:
                if pair[1] == b:
                    pair[0] = vn.get(pair[0], pair[0])
    for child in b.children:
        dvnt(child, vn.copy())


