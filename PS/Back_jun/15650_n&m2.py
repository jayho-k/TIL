'''
4 2
'''

tmp = []
def dfs(d,idx):
    if d == m:
        print(*tmp)
        return

    for i in range(idx,n):
        if not visited[i]:
            tmp.append(lst[i])
            visited[i]=1
            dfs(d+1,i+1)
            visited[i]=0
            tmp.pop()


n,m = map(int,input().split())
visited = [0]*n
lst = list(range(1,n+1))


dfs(0,0)