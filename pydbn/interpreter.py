import sys




stack = []
bytecode = []
env = {}

for line in sys.stdin:
    n, o, a = line.strip().split()
    bytecode.append((o, a))

pointer = 0
while pointer < len(bytecode):
    print pointer, stack, env

    op, arg = bytecode[pointer]
    print '%s %s' % (op, arg)
    
    if op == 'STORE':
        env[arg] = stack.pop()
        pointer += 1
    
    elif op == 'LOAD':
        stack.append(env[arg])
        pointer += 1
    
    elif op == 'LOAD_INTEGER':
        stack.append(int(arg))
        pointer += 1

    elif op == 'SET_DOT':
        pointer += 1
    
    elif op == 'GET_DOT':
        pointer += 1
        
    elif op == 'BINARY_ADD':
        top = stack.pop()
        top1 = stack.pop()
        stack.append(top + top1)
        pointer += 1
    
    elif op == 'BINARY_SUB':
        top = stack.pop()
        top1 = stack.pop()
        stack.append(top - top1)
        pointer += 1
    
    elif op == 'BINARY_DIV':
        top = stack.pop()
        top1 = stack.pop()
        stack.append(top / top1)
        pointer += 1
    
    elif op == 'BINARY_MUL':
        top = stack.pop()
        top1 = stack.pop()
        stack.append(top * top1)
        pointer += 1
    
    elif op == 'COMPARE_SAME':
        top = stack.pop()
        top1 = stack.pop()
        stack.append(int(top == top1))
        pointer += 1
        
    elif op == 'COMPARE_NSAME':
        top = stack.pop()
        top1 = stack.pop()
        stack.append(int(top != top1))
        pointer += 1
    
    elif op == 'COMPARE_SMALLER':
        top = stack.pop()
        top1 = stack.pop()
        stack.append(int(top < top1))
        pointer += 1
    
    elif op == 'COMPARE_NSMALLER':
        top = stack.pop()
        top1 = stack.pop()
        stack.append(int(top >= top1))
        pointer += 1
    
    elif op == 'DUP_TOPX':
        c = int(arg)
        dups = stack[-c:]
        stack.extend(dups)
        pointer += 1
    
    elif op == 'POP_TOPX':
        c = int(arg)
        for i in range(c):
            stack.pop()
        pointer += 1
    
    elif op == 'ROT_TWO':
        top = stack.pop()
        top1 = stack.pop()
        stack.append(top)
        stack.append(top1)
        pointer += 1
    
    elif op == 'JUMP':
        target = int(arg)
        pointer = target
    
    elif op == 'POP_JUMP_IF_FALSE':
        target = int(arg)
        top = stack.pop()
        if not top:
            pointer = target
        else:
            pointer += 1
    
    elif op == 'POP_JUMP_IF_TRUE':
        target = int(arg)
        top = stack.pop()
        if top:
            pointer = target
        else:
            pointer += 1

print pointer, stack, env
print 'END'
    