def postfix(inpt):

    oostack = []
    stack = []
    tokens = list(inpt)
    oper = ['+','-','*','/','(',')']

    for token in tokens:

        if token not in oper:
            oostack.append(token)

        elif token == '(':
            stack.append('(')

        elif token == ')':
            while  1:
                s = stack.pop()
                oostack.append(s)
                if stack[-1] == '(':
                    stack.pop()
                    break

        elif token in oper:
            if token == '*' or token == '/':
                stack.append(token)

            elif token == '+' or token =='-':
        
                if '(' not in stack:
                    if '*' in stack or '/' in stack:
                        while stack != []:
                            s = stack.pop()
                            oostack.append(s)
                stack.append(token)

    else:
        while stack != []:
            s = stack.pop()
            oostack.append(s)

    return oostack


i = input()
s = postfix(i)
print(''.join(s))