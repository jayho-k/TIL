'''
계산기 만들기
순서
1. 각각을 토큰으로 만들어준다 (연산자와 피연산자를 나누기 위해서)
2. infix ==> postfix
3. 계산

2번 방법
(2+5) * 7 ==> 2 5 + 7 * 이런식으로 바꿔준다

items를 쓰는 이유에 대해서

'''

class Stack:

    def __init__(self):
        self.items = []

    def push(self, var):
        self.items.append(var)

    def pop(self):
        self.items.pop()

    def top(self):
        return self.items[-1]

    def __len__(self):
        cnt = 0
        for _ in self.items:
            cnt += 1
        return cnt

# infix => postfix로 만들기
# 입력
inpt = '(2+5)*7'

def postfix(s):

    oostack = []
    stack = Stack()
    tokens = list(inpt)
    oper = ['+','-','*','/','(',')']

    for token in tokens:

        if token not in oper:
            oostack.append(token)

        elif token == '(':
            stack.push('(')

        elif token == ')':
            while 1:
                if stack.top() == '(':
                    break

                oostack.append(stack.top())
                stack.pop()

        elif token in oper:
            if token == '*' or token == '/':
                while 1:
                    stack.pop()
                    if stack.items == []:
                        break
                stack.push(token)

            elif token == '+' or token =='-':
                stack.push(token)

    else:
        while stack.items != []:
            oostack.append(stack.top())
            stack.pop()

    return oostack

def calculator(psfx):
    stack = []
    for ps in psfx:
        if ps == '+':
            cal = (stack.pop()) + (stack.pop())
            stack.append(cal)

        elif ps == '-':
            cal = (stack.pop()) - (stack.pop())
            stack.append(cal)

        elif ps == '*':
            cal = (stack.pop()) * (stack.pop())
            stack.append(cal)

        elif ps == '/':
            m = stack.pop()
            cal = stack.pop() / m
            stack.append(cal)

        else:
            stack.append(int(ps))

    return(stack.pop())

psfx = postfix(inpt)
print(psfx)
print(calculator(psfx))