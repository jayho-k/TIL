'''
5
10 -1
10 1 -1
4 1 -1
4 3 1 -1
3 3 -1

걸리는 시간, 먼저 지어져야하는 건물들의 번호


'''

n = int(input())

graph = [[] for _ in range(n+1)]

for i in range(1,n+1):
    time, *lst = map(int,input().split())
    graph[i].append(time)
    graph[i].append(lst)

print(graph)

for g in range(1,len(graph)):
    for l in graph[g][1]:
        print(l)