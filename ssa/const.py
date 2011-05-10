from ssa import *

TOP = "TOP"
BOTTOM = "BOTTOM"

def meet(v1, v2):
    if v1 == v2:
        return v1
    if v1 == TOP:
        return v2
    if v2 == TOP:
        return v1
    return BOTTOM

def arith(op, v1, v2):
    if v1 == BOTTOM or v2 == BOTTOM:
        return BOTTOM
    if v1 == TOP or v2 == TOP:
        return TOP
    return eval("%s %s %s" % (v1, op, v2))

def def_uses(blocks):
    vars = []
    defs = {}
    uses = {}
    for b in blocks:
        for (var, pairs) in b.phis.items():
           if var not in vars:
	       vars.append(var)
	   defs[var] = ["phi", var, pairs]
	   for pair in pairs:
               if pair[0] not in vars:
                   vars.append(pair[0])
	       if pair[0] not in uses:
	           uses[pair[0]] = []
	       uses[pair[0]].append((defs[var], b))
	for op in b.ops:
            tag = op[0]
	    if tag == "br":
	        break
	    elif tag == "brc" or tag == "return":
	        if is_var(op[1]):
	            if op[1] not in uses:
		        uses[op[1]] = []
		    uses[op[1]].append((op,b))
	    else:
	        dest = op[1]
	        if dest not in vars:
		    vars.append(dest)
		defs[dest] = op
		if op[0] != "=":
		    if is_var(op[3]):
		        if op[3] not in uses:
		            uses[op[3]] = []
		        uses[op[3]].append((op,b))
		if is_var(op[2]):
		    if op[2] not in uses:
		       uses[op[2]] = []
		    uses[op[2]].append((op,b))
    return (vars, defs, uses)
	 
def sscp(var, defs, uses):
    values = {}
    wl = []
    for v in var:
        op = defs.get(v, None)
        if op and op[0] == "=" and not is_var(op[2]):
            values[v] = int(op[2])
	    wl.append(v)
	else:
	    values[v] = TOP
    while len(wl) > 0:
        v = wl.pop(0)
        for (use, block) in uses.get(v, []):
	    if use[0] == "=":
	        val = values[use[2]]
	    elif use[0] == "phi":
	        val = TOP
	        pairs = use[2]
	        for pair in pairs:
		    val = meet(val, values[pair[0]])
            elif use[0] == "brc" or use[0] == "return":
	        continue
	    else:
	        left = is_var(use[2]) and values[use[2]] or int(use[2])
	        right = is_var(use[3]) and values[use[3]] or int(use[3])
	        val = arith(use[0], left, right)
	    if val != values[use[1]]:
	        values[use[1]] = val
	        wl.append(use[1])
    return values


def sccp(blocks, vars, uses):
    cfgwl = [blocks[0]]
    usewl = []
    values = {}
    for var in vars:
        values[var] = TOP
    for b in blocks:
        b.live = False
    while len(cfgwl) > 0 or len(usewl) > 0:
        while len(cfgwl) > 0:
            b = cfgwl.pop(0)
            if b.live:
                continue
            b.live = True
            for (var, pairs) in b.phis.items():
                val = TOP
                for pair in pairs:
                    val = meet(val, values[pair[0]])
                values[var] = val
                for (use, block) in uses.get(var, []):
                    if block.live:
                        usewl.append(use)
            for op in b.ops:
                tag = op[0]
                if tag == "br":
                    cfgwl.append(op[1])
                elif tag == "brc":
                    cond = values[op[1]]
                    if cond == BOTTOM:
                        cfgwl.append(op[2])
                        cfgwl.append(op[3])
                    elif cond:
                        cfgwl.append(op[2])
                    else:
                        assert cond != TOP
                        cfgwl.append(op[3])
                elif tag == "return":
                    continue
                elif tag == "=":
                    values[op[1]] = is_var(op[2]) and values[op[2]] or int(op[2])
                    for (use, block) in uses.get(op[1], []):
                        if block.live:
                            usewl.append(use)
                else:
                    left = is_var(op[2]) and values[op[2]] or int(op[2])
                    right = is_var(op[3]) and values[op[3]] or int(op[3])
                    values[op[1]] = arith(tag, left, right)
                    for (use, block) in uses.get(op[1], []):
                        if block.live:
                            usewl.append(use)
        while len(usewl) > 0:
            use = usewl.pop(0)
            if use[0] == "=":
	        val = is_var(use[2]) and values[use[2]] or int(use[2])
	    elif use[0] == "phi":
	        val = TOP
	        pairs = use[2]
	        for pair in pairs:
		    val = meet(val, values[pair[0]])
            elif use[0] == "brc":
                cond = values[use[1]]
                if cond == BOTTOM:
                    cfgwl.append(use[2])
                    cfgwl.append(use[3])
                continue
            elif use[0] == "return":
	        continue
	    else:
	        left = is_var(use[2]) and values[use[2]] or int(use[2])
	        right = is_var(use[3]) and values[use[3]] or int(use[3])
	        val = arith(use[0], left, right)
	    if val != values[use[1]]:
	        values[use[1]] = val
	        for (use, block) in uses.get(use[1], []):
                    if block.live:
                        usewl.append(use)
    return values


def rewrite(uses, values):
    for (var, val) in values.items():
        if val != BOTTOM:
            for (op, block) in uses.get(var, []):
                if not block.live:
                    continue
                if op[0] == "=":
                    op[2] = val
                elif op[0] == "return":
                    op[1] = val
                elif op[0] == "brc":
                    assert val != TOP
                    if val:
                        op[0] = "br"
                        op[1] = op[2]
                        del op[2]
                        del op[2]
                    else:
                        op[0] = "br"
                        op[1] = op[3]
                        del op[2]
                        del op[2]
                elif op[0] == "phi":
                    for pair in op[2]:
                        if pair[0] == var:
                            pair[0] = val
                else:
                    if op[2] == var:
                        op[2] = val
                    if op[3] == var:
                        op[3] = val
                    if not is_var(op[2]) and not is_var(op[3]):
                        op[2] = arith(op[0], op[2], op[3])
                        op[0] = "="
                        del op[3]
