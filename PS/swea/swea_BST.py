'''



'''
import math


def in_order(node):

    if tree[node][0] !=0: in_order(tree[node][0])

    in_lst.append(node)

    if tree[node][1] !=0: in_order(tree[node][1])

T = int(input())
for tc in range(1, T+1):
    n = int(input())
    lst = list(range(1,n+1))
    tree = [[] for _ in range(n+1)]

    for i in range(1,len(lst)+1):
        p = i
        ch1 = 2*i
        ch2 = 2*i+1
        if ch1 <= n:
            tree[p].append(ch1)
            if ch2 <=n:
                tree[p].append(ch2)
            else:
                tree[p].append(0)
        else:
            tree[p].append(0)
            tree[p].append(0)

    in_lst = []
    in_order(1)
    ans = [0]*(n+1)
    j = 0
    for i in in_lst:
        j += 1
        ans[i] = j

    print(f'#{tc} {ans[1]} {ans[n//2]}')




# import math
# def mk_bst(lst,s):
#     if s == h:
#         print(tree)
#         return
#     if len(lst) == 0:
#         return
    
#     m = len(lst)//2
#     tree[s].append(lst[m])
    
#     mk_bst(lst[:m],s+1)
#     mk_bst(lst[m+1:],s+1)

    

# T = 1
# for tc in range(1, T+1):
#     n = int(input())

#     lst = list(range(1,n+1))
#     h = math.ceil(math.log2(len(lst)))
#     tree = [[] for _ in range(h+1)]

#     mk_bst(lst,0)
#     print(h)
#     print(tree)
    
#     # 1 2 3 4 5 6 7 ==> 0 1 2 3 4 5 6
#     # 4
#     # 

