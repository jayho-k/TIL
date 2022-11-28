'''

4 2
'''

tmp = []
def dfs(d):

    if d==m:
        print(*tmp)
        return

    for i in range(n):
        if not visited[i]:
            visited[i]=1
            tmp.append(lst[i])
            dfs(d+1)
            visited[i]=0
            tmp.pop()


n,m = map(int,input().split())
visited = [0]*n
lst = list(range(1,n+1))

dfs(0)