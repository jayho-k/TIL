'''


'''

def bfs(x):
    
    q = deque([x])
    visited[x] = 1

    while q:
        new = q.popleft()

        for i in grid[new]:
            if visited[i]==0:
                visited[i] += visited[new]+1
                q.append(i)



from collections import deque

n,m,k,x = map(int,input().split())

grid = [[] for _ in range(n+1)]
visited = [0]*(n+1)


for _ in range(m):
    s,f = map(int,input().split())
    grid[s].append(f)


bfs(x)

ans = []
for i in range(n+1):
    if visited[i] == k+1:
        ans.append(i)

if ans == []:
    print(-1)
else:
    ans.sort()
    for a in ans:
        print(a)












# def dfs(d,x):

#     if d == k:
#         print(x)
#         return

#     for g in grid[x]:
#         dfs(d+1, g)


# n,m,k,x = map(int,input().split())

# grid = [[] for _ in range(n+1)]

# for _ in range(m):
#     s,f = map(int,input().split())
#     grid[s].append(f)

# print(grid)
# dfs(0,x)