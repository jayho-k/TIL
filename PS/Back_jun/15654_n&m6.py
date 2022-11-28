'''
4 2
9 8 7 1
'''

tmp = []
def dfs(d,idx):

    if d == m:
        print(*tmp)



    for i in range(idx,n):
        if not visited[i]:

            tmp.append(lst[i])
            visited[i] = 1
            dfs(d+1,i+1)
            visited[i] = 0
            tmp.pop()



n,m = map(int,input().split())
lst = list(map(int,input().split()))
lst.sort()
visited = [0]*n
dfs(0,0)