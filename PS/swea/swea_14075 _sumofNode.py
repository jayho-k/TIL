'''


5 3 2
4 1
5 2
3 3

1
10 5 2
8 42
9 468
10 335
6 501
7 170
'''
def search(p_i):
    
    if p_i > n_num:
        return 0

    if tree[p_i] == 0:
        return search(p_i*2)+search(p_i*2+1)

    else:
        return tree[p_i]


T = int(input())
for tc in range(1,T+1):

    n_num, l_num, t = map(int, input().split())
    tree = [0] * (n_num+1)

    for _ in range(l_num):
        leaf, leaf_v = map(int, input().split())
        tree[leaf] = leaf_v

    ans = search(t)
    print(ans)



# T = int(input())
# T = int(input())
# for tc in range(1,T+1):

#     # 노드, 리프노드, 노드번호
#     n,l,node_num = map(int, input().split())
#     tree = [0]*(n+2)

#     for i in range(l):
#         l_num, num = map(int,input().split())
#         tree[l_num] = num

#     for i in range(n,0,-1):
#         if tree[i] == 0:
#             tree[i] = tree[i*2]+tree[i*2+1]
    
#     print(f'#{tc} {tree[node_num]}')


# def dfs(now):
#     if now>n_num:
#         print(tree)
#         return 0

#     if tree[now] == 0: # 저장된 값이 없으면 자식들끼리 더하고 리턴
#         print(tree)
#         return dfs(now*2) + dfs(now*2+1)

#     else:
#         # 리프노드 이면 리프노드 리턴
#         print(tree)
#         return tree[now]


# T = int(input())
# for tc in range(1,T+1):

#     n_num, l_num, t = map(int, input().split())
#     tree = [0] * (n_num+1)

#     for _ in range(l_num):
#         leaf, leaf_v = map(int, input().split())
#         tree[leaf] = leaf_v
#     print(tree)


#     ans = dfs(t)
#     print(ans)



