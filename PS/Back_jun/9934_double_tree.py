'''
3
1 6 4 3 5 2 7

0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
'''
n = int(input())
lst = list(map(int, input().split()))

tree = [[] for _ in range(n)]
def mk_tree(lst, s):
    m = len(lst)//2
    tree[s].append(lst[m])

    if len(lst)==1:
        return

    mk_tree(lst[:m],s+1)
    mk_tree(lst[m+1:],s+1) 

mk_tree(lst,0)

for t in tree:
    print(*t)

