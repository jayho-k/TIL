'''


1. 후위 순위 => 트리(항상 노드만 저장)
=> 트리를 저장할때는 leaf노드에는 0,0을 저장한다.
=> 트리를 저장할떄는 항상 노드만 저장한다. => Value는 따로 만들어 준다
=> 

2. 후위 연산
=> 후위연산을 할 경우에는 stack을 사용한다.
=> 숫자는 append
=> 연산자는 두번의 pop을 통해서 계산 => append



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

def post_travel(node):
    
    if graph[node][0]!=0:
        post_travel(graph[node][0])

    if graph[node][1]!=0:
        post_travel(graph[node][1])

    post_oper.append(oper[node])

def post_operation():
    store = []
    for po in post_oper:
        if po=='+':
            store.append(store.pop()+store.pop())

        elif po=='-':
            store.append(-(store.pop()-store.pop()))

        elif po=='*':
            store.append(store.pop()*store.pop())

        elif po=='/':
            a = store.pop()
            b = store.pop()
            store.append(b/a)

        else:
            store.append(int(po))
    return store[0]


for tc in range(1,11):
    n = int(input())
    graph = [[] for _ in range(n+1)]
    oper = [0]
    post_oper = []

    # setting
    for _ in range(n):
        input_node = tuple(input().split())
        if len(input_node)==4:
            node,o,c1,c2 = input_node
            graph[int(node)].append(int(c1))
            graph[int(node)].append(int(c2))
            oper.append(o)

        else:
            node,v = input_node
            graph[int(node)].append(0)
            graph[int(node)].append(0)
            oper.append(v)

    post_travel(1)
    # print(post_oper)
    ans = post_operation()
    print(f"#{tc} {int(ans)}")



# def dfs(node):

#     if graph[node][0]!=0:
#         dfs(graph[node][0])

#     if graph[node][1]!=0:
#         dfs(graph[node][1])

#     post_lst.append(oper[node])

# def post_oper(post_lst):

#     stack = []
#     for p in post_lst:
#         if p=='+':
#             stack.append(stack.pop()+stack.pop())

#         elif p=='-':
#             stack.append(-(stack.pop()-stack.pop()))

#         elif p=='*':
#             stack.append(stack.pop()*stack.pop())

#         elif p=='/':
#             a = stack.pop()
#             b = stack.pop()
#             stack.append(b/a)

#         else:
#             stack.append(int(p))

#     return stack

# for tc in range(1,3):
#     n = int(input())
#     graph = [[] for _ in range(n+1)]
#     oper = [0]
#     post_lst = []
#     for _ in range(n):
#         input_tmp = list(input().split())
#         if len(input_tmp)==4:
#             s,o,l,r = input_tmp
#             graph[int(s)].append(int(l))
#             graph[int(s)].append(int(r))
#             oper.append(o)
#         else:
#             s,v = input_tmp
#             graph[int(s)].append(0)
#             graph[int(s)].append(0)
#             oper.append(v)
#     dfs(1)
#     stack = post_oper(post_lst)
#     print(f"#{tc} {int(stack[0])}")
