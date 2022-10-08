'''
4 2
9 8 7 1
'''

tmp = []
def dfs(d):

    if d == m:
        print(*tmp)
        return

    for i in range(n):
        tmp.append(lst[i])
        dfs(d+1)
        tmp.pop()

n,m = map(int,input().split())
lst = list(map(int,input().split()))
lst.sort()

dfs(0)