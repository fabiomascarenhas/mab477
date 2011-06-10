import re

class BasicBlock:
    def __init__(self, name):
        self.name = name
        self.phis = {}
        self.ops = []
        self.succs = []
        self.preds = []
        self.vars = set()
    def add_phi(self, var):
        if var not in self.phis:
            pairs = []
            for b in self.preds:
                pairs.append([var, b])
            self.phis[var] = pairs
            return True
        else:
            return False
    def br(self, b):
        self.succs = [b]
        self.ops.append(["br", b])
        b.preds.append(self)
    def brc(self, var, bt, bf):
        self.succs = [bt, bf]
        self.ops.append(["brc", var, bt, bf])
        bt.preds.append(self)
        bf.preds.append(self)
    def mov(self, dest, orig):
        self.vars.add(dest)
        self.ops.append(["=", dest, orig])
    def ret(self, val):
        self.ops.append(["return", val])
    def __call__(self, str):
        ops = str.split("\n")
        for op in ops:
            m = re.search('^[ ]*([a-zA-Z0-9]+)[ ]*=[ ]*([a-zA-Z0-9]+)[ ]*([^a-zA-Z0-9 ]+)[ ]*([a-zA-Z0-9]+)$', op)
            if m == None:
                m = re.search('^[ ]*([a-zA-Z0-9]+)[ ]*=[ ]*([a-zA-Z0-9]+)$', op)
                if m != None:
                    self.mov(m.group(1), m.group(2))
            else:
                self.op(m.group(1), m.group(2), m.group(3), m.group(4))
    def op(self, dest, left, op, right):
        self.vars.add(dest)
        self.ops.append([op, dest, left, right])
    def __str__(self):
        name = "%-5s" % (self.name + ":")
        insts = []
        for var in self.phis.keys():
            pairs = self.phis[var]
            phi = (var, pairs[0][0], pairs[0][1].name, pairs[1][0], pairs[1][1].name)
            insts.append("%s = phi(%s[%s], %s[%s])" % phi)
        for op in self.ops:
            if op[0] == "=":
                insts.append("%s = %s" % (op[1], op[2]))
            elif op[0] == "br":
                insts.append("br %s" % op[1].name)
            elif op[0] == "brc":
                insts.append("brc %s => %s, %s" % (op[1], op[2].name, op[3].name))
            elif op[0] == "return":
                insts.append("return %s" % op[1])
            else:
                insts.append("%s = %s %s %s" % (op[1], op[2], op[0], op[3]))
        return name + ("\n" + " " * 5).join(insts)

def rpo(nodes):
    marks = {}
    n = [len(nodes)-1]
    rpo = [0] * len(nodes)
    def bfs_visit(node):
        marks[node] = True
        for child in node.succs:
            if not marks.get(child, False):
                bfs_visit(child)
        node.rpo = n[0]
        rpo[node.rpo] = node
        n[0] -= 1
    bfs_visit(nodes[0])
    return rpo

def intersect(left, right):
    finger1 = left
    finger2 = right
    while finger1 != finger2:
        while finger1.rpo > finger2.rpo:
            finger1 = finger1.idom
        while finger2.rpo > finger1.rpo:
            finger2 = finger2.idom
    return finger1

def dom_tree(nodes):
    for node in nodes:
        node.children = []
        node.idom = None
    nodes_rpo = rpo(nodes)
    nodes[0].idom = nodes[0]
    for i in range(1, len(nodes_rpo)):
        if len(nodes_rpo[i].preds) == 2 and nodes_rpo[i].preds[1].idom != None:
            nodes_rpo[i].idom = intersect(nodes_rpo[i].preds[0], nodes_rpo[i].preds[1])
            nodes_rpo[i].idom.children.append(nodes_rpo[i])
        else:
            nodes_rpo[i].idom = nodes_rpo[i].preds[0]
            nodes_rpo[i].idom.children.append(nodes_rpo[i])
    for node in nodes:
        node.children.sort(key = lambda node: node.name)

def dom_frontier(nodes):
    for n in nodes:
        n.df = set()
    for n in nodes:
        if len(n.preds) > 1:
            for p in n.preds:
                # Add n to the frontier of nodes
                # that dominate p but do not dominate n
                runner = p
                while runner != n.idom:
                    runner.df.add(n)
                    runner = runner.idom

def find_globals(nodes):
    blocks = {}
    for n in nodes:
        for var in n.vars:
            if not var in blocks:
                blocks[var] = set()
    globals = set()
    for n in nodes:
        locals = set()
        for i in range(len(n.ops)-1):
            op = n.ops[i]
            if op[0] != "=" and op[3] in blocks and op[3] not in locals:
                globals.add(op[3])
            if op[2] in blocks and op[2] not in locals:
                globals.add(op[2])
            locals.add(op[1])
            blocks[op[1]].add(n)
        jump = n.ops[-1]
        if jump != "br":
            if jump[1] in blocks and jump[1] not in locals:
                globals.add(jump[1])
    return (globals, blocks)

def add_phis(globals, blocks):
    for var in globals:
        worklist = list(blocks[var])
        while len(worklist) > 0:
            block = worklist.pop(0)
            for frontier in block.df:
                if frontier.add_phi(var):
                    worklist.append(frontier)

def old_name(ssa_name):
    match = re.match("^(.+)_[0-9]+$", ssa_name)
    return match.group(1)

def is_var(arg):
    try:
        x = int(arg)
        return False
    except ValueError:
        return True

def ssa_name(name, i):
    return "%s_%s" % (name, i)

def new_name(name, counter, stack):
    i = counter[name]
    counter[name] += 1
    stack[name].append(i)
    return ssa_name(name, i)

def rename(b, counter, stack):
    for var in b.phis.keys():
        pairs = b.phis[var]
        del b.phis[var]
        newvar = new_name(var, counter, stack)
        b.phis[newvar] = pairs
    for i in range(len(b.ops)-1):
        op = b.ops[i]
        if op[0] != "=":
            if is_var(op[3]):
                op[3] = ssa_name(op[3], stack[op[3]][-1])
        if is_var(op[2]):
            op[2] = ssa_name(op[2], stack[op[2]][-1])
        op[1] = new_name(op[1], counter, stack)
    jump = b.ops[-1]
    if (jump[0] == "brc" or jump[0] == "return") and is_var(jump[1]):
        jump[1] = ssa_name(jump[1], stack[jump[1]][-1])
    for succ in b.succs:
        for var in succ.phis.keys():
            pairs = succ.phis[var]
            for pair in pairs:
                if pair[1] == b:
                    if len(stack[pair[0]]) == 0:
                        stack[pair[0]].append(0)
                        counter[pair[0]] += 1
                    pair[0] = ssa_name(pair[0], stack[pair[0]][-1])
    for child in b.children:
        rename(child, counter, stack)
    for i in range(len(b.ops)-1):
        op = b.ops[i]
        stack[old_name(op[1])].pop()
    for var in b.phis.keys():
        stack[old_name(var)].pop()

def ssa_rename(blocks):
    counter = {}
    stack = {}
    for b in blocks:
        for var in b.vars:
            if var not in counter:
                counter[var] = 0
            if var not in stack:
                stack[var] = []
    rename(blocks[0], counter, stack)


def print_cfg(b):
    for block in b:
        print str(block)

def full_ssa(b):
    dom_tree(b)
    dom_frontier(b)
    globals, blocks = find_globals(b)
    add_phis(globals, blocks)
    ssa_rename(b)
