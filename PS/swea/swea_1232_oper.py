'''

5
1 - 2 3
2 - 4 5
3 10
4 88
5 65

'''
import math
# import sys
# sys.stdin = open('oper.txt')

T= 10
for tc in range(1,T+1):
    n = int(input())
    tree = [0] *(n+1)
    save = [0]

    for i in range(n):
        l = list(input().split())
        if len(l) == 4:
            tree[int(l[0])] = l[1]
            save.append((int(l[0]),int(l[2]),int(l[3])))

        else:
            tree[int(l[0])] = int(l[1])
            save.append(0)

    # print(save)
    for i in range(n,0,-1):

        if save[i] != 0:
            p = save[i][0]
            ch1 = save[i][1]
            ch2 = save[i][2]

            # if tree[p] in ['+','-','*','/']:
            if tree[p] == '+' : tree[p] = tree[ch1]+tree[ch2]
            if tree[p] == '-' : tree[p] = tree[ch1]-tree[ch2]
            if tree[p] == '*' : tree[p] = tree[ch1]*tree[ch2]
            if tree[p] == '/' : tree[p] = tree[ch1]/tree[ch2]
            # print(tree)

    # print(tree)
    print(f'#{tc} {int(tree[1])}')
            





















# def in_order(node):

#     if tree[node][0] != 0:
#         lst.append('(')
#         in_order(tree[node][0])

#     lst.append(node)

#     if tree[node][1] != 0:
#         in_order(tree[node][1])
#         lst.append(')')

# T = 1
# for tc in range(1,T+1):
#     n = int(input())
#     h = math.ceil(math.log2(n))

#     tree = [[] for _ in range(n+1)]
#     oper_lst = []

#     for i in range(n):
#         l = list(input().split())
#         nl = len(l)
#         if nl == 4:
#             node, op, left,right = l
#             node = int(node)
#             left = int(left)
#             right = int(right)
#             tree[node].append(left)
#             tree[node].append(right)
#             oper_lst.append((node,op))

#         else:
#             node, v = l
#             node = int(node)
#             v = int(v)
#             tree[node].append(0)
#             tree[node].append(0)
#             oper_lst.append((node,v))

#     lst = []
#     in_order(1)
#     for nn, o in oper_lst:
#         lst[lst.index(nn)] = o



    # total = lst[0]
    # print(tree)
    # print(lst)
    # for i in range(1,len(lst),2):

    #     if lst[i] == '+':
    #         total += lst[i+1]

    #     if lst[i] == '-':
    #         total -= lst[i+1]

    #     if lst[i] == '*':
    #         total *= lst[i+1]

    #     if lst[i] == '/':
    #         total /= lst[i+1]

    # print(f'# {tc} {int(total)}')