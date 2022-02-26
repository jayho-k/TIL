'''
6 5
1 4
1 3
2 3
2 5
4 6


7 4
1 6
2 3
2 6
3 5
1 5
'''

def gr(graph, e):
    for _ in range(e):
        n1, n2 = map(int, input().split())
        graph[n1].append(n2)
        graph[n2].append(n1)

T = 1
for tc in range(1, T+1):
    q = []
    v, e = map(int, input().split())

    # 그래프
    graph = [[] for _ in range(v+1)]
    visited = [0]*(v+1)
    gr(graph, e)

    s, g = map(int, input().split())

    # bfs 구현
    visited[s] = 1
    q.append(s)
    while q: # q가 빌때까지
        t = q.pop(0)

        for i in graph[t]:
            if visited[i] == 0:
                visited[i] = visited[t] + 1
                q.append(i)
                print(visited)

    if visited[g] == 0:
        print(f'#{tc} {0}')
    else:
        print(f'#{tc} {visited[g]-1}')
    

