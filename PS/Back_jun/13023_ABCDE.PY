'''
a걸치고 b걸치고 ===> e까지 갈수 있니??

5 4
0 1
1 2
2 3
3 4

6 5
0 1
0 2
0 3
0 4
0 5

5 5
0 1
1 2
2 3
3 0
1 4


vistied가 1로 갔을때도 있어야 하고 3으로 갈때도 해줘함
'''
import sys

def dfs(d,st):
    global ans

    if ans == 1:
        return

    if d == 4:
        ans = 1
        return

    for i in graph[st]:
        if visited[i] == 0:
            visited[i] = 1
            dfs(d+1, i)
            visited[i] = 0

input = sys.stdin.readline
n, m = map(int, input().split())
graph = [[] for _ in range(n)]

for _ in range(m):
    s, f = map(int, input().split())
    graph[s].append(f)
    graph[f].append(s)

ans = 0
for j in range(len(graph)):
    visited = [0]*n
    visited[j] = 1
    dfs(0,j)

print(ans)
