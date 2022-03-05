'''
1. 그래프 설정


7
6
1 2
2 3
1 5
5 2
5 6
4 7

'''
c = int(input())
n = int(input())

graph = [[] for _ in range(c+1)]

for i in range(n):
    s,g = map(int, input().split())
    graph[s].append(g)
    graph[g].append(s)

visited = [0]*(c+1)
s = []

visited[1]=1
s.append(1)

while s:
    t = s.pop()
    for i in graph[t]:
        if visited[i] == 0:
            visited[i] = 1
            s.append(i)

cnt = visited.count(1) - 1
print(cnt)













