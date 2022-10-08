'''
3 3

'''

tmp = []
def dfs(d,idx):

    if d == m:
        print(*tmp)
        return

    for i in range(idx,n):
        if not visited[i]:
            tmp.append(lst[i])
            dfs(d+1,i)
            tmp.pop()


n,m = map(int,input().split())
lst = list(range(1,n+1))
visited = [0]*n


dfs(0,0)

