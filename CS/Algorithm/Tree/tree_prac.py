'''
8
1 W 2 3
2 F 4 5
3 R 6 7
4 O 8
5 T
6 A
7 E
8 S
'''
import sys
sys.stdin = open('input.txt')

def in_order(node):
    
    if graph[node][0] !=0: in_order(graph[node][0])
    lst.append(node)
    if graph[node][1] !=0: in_order(graph[node][1])

T = 10
for tc in range(1,T+1):

    n = int(input())
    lst = []
    tree_num = []
    alph = [0]
    graph = [[] for _ in range(n+1)]

    for i in range(n):
        l = list(input().split())
        if len(l) == 4:
            tn, a, ch1, ch2 = l
            tn = int(tn)
            ch1 = int(ch1)
            ch2 = int(ch2)
            tree_num.append(tn)
            alph.append(a)
            graph[tn].append(ch1)
            graph[tn].append(ch2)

        elif len(l) == 3:
            tn, a, ch1 = l
            tn = int(tn)
            ch1 = int(ch1)
            tree_num.append(int(tn))
            alph.append(a)
            graph[tn].append(ch1)
            graph[tn].append(0)

        elif len(l) == 2:
            tn, a = l
            tn = int(tn)
            tree_num.append(int(tn))
            alph.append(a)
            graph[tn].append(0)
            graph[tn].append(0)

    lst = []
    in_order(1)
    ans = []
    for l in lst:
        ans.append(alph[l])

    a = ''.join(ans)
    print(f'#{tc} {a}')










# def in_order(v):

#     if v:
#         in_order(2*v+1)
#         print(v)
#         in_order(2*v+2)

# n = int(input())
# lst = []
# for i in range(n):
#     a = input().split()
#     lst.append(a)

# tree_num = []
# alph = []

# for l in lst:
#     if len(l) == 4:
#         tn, a, ch1, ch2 = l
#         tree_num.append(int(tn))
#         alph.append(a)

#     elif len(l) == 3:
#         tn, a, ch1 = l
#         tree_num.append(int(tn))
#         alph.append(a)

#     elif len(l) == 2:
#         tn, a = l
#         tree_num.append(int(tn))
#         alph.append(a)

# print(tree_num)
# print(alph)
# in_order(0)