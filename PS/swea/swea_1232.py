'''


후위 순위

5
1 - 2 3
2 - 4 5
3 10
4 88
5 65
7
1 / 2 3
2 - 4 5
3 - 6 7
4 261
5 61
6 81
7 71
'''

def dfs(node):

    if graph[node][0]!=0:
        dfs(graph[node][0])

    if graph[node][1]!=0:
        dfs(graph[node][1])

    post_lst.append(oper[node])

def post_oper(post_lst):

    stack = []
    for p in post_lst:
        if p=='+':
            stack.append(stack.pop()+stack.pop())

        elif p=='-':
            stack.append(-(stack.pop()-stack.pop()))

        elif p=='*':
            stack.append(stack.pop()*stack.pop())

        elif p=='/':
            a = stack.pop()
            b = stack.pop()
            stack.append(b/a)

        else:
            stack.append(int(p))

    return stack

for tc in range(1,3):
    n = int(input())
    graph = [[] for _ in range(n+1)]
    oper = [0]
    post_lst = []
    for _ in range(n):
        input_tmp = list(input().split())
        if len(input_tmp)==4:
            s,o,l,r = input_tmp
            graph[int(s)].append(int(l))
            graph[int(s)].append(int(r))
            oper.append(o)
        else:
            s,v = input_tmp
            graph[int(s)].append(0)
            graph[int(s)].append(0)
            oper.append(v)
    dfs(1)
    stack = post_oper(post_lst)
    print(f"#{tc} {int(stack[0])}")
