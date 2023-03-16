'''
이 문제도 점마다 거리가 얼마나 포함되었는지 확인하는 문제
따라서 그떄그때마다 값을 저장하는 것이 필요
lst 에 값을 저장해서 진행해 보자

bfs
1. 한 사이클 마다 값의 변화를 알고 싶을 경우
q = deque([(y,x,cnt)]) => 큐에 cnt를 사용한다.

2. visited를 사용에 값을 저장할 경우
    그떄그때마다 값을 저장하는 것이 필요할때
    이전의 값이 필요할 경우 선택한다.

3. bfs사용시 주의할 점
    # bfs에서 q.append()를 할때는 무조건 조건이 있어야한다.
    # 만약 조건이 없을 경우에는 무한루프에 빠질 가능성이 높다.

3
1
2 3
0 1 1
0 2 6
1 2 1

1
4 7
0 1 9
0 2 3
0 3 7
1 4 2
2 3 8
2 4 1
3 4 8

1
4 6
0 1 10
0 2 7
1 4 2
2 3 10
2 4 3
3 4 10

'''
from collections import deque


def bfs(st,ed):

    q = deque([(st)])

    # 언제 마다 값을 저장?
    # 도시마다 거리를 저장해줄 것 => 최소 거리
    v = [0]+[1e9]*(n)

    while q:
        e = q.popleft()
        for ne,nw in graph[e]:
            
            if v[ne] > v[e]+nw: 
                # 이것을 사용하지 않을 경우 무한 루프에 빠질수 있음
                # bfs에서 q.append()를 할때는 무조건 조건이 있어야한다.
                v[ne] = v[e]+nw    
                q.append(ne)

    return v[-1]

for tc in range(1,int(input())+1):

    n,E = map(int,input().split())
    graph = [[] for _ in range(n+1)]
    for _ in range(E):
        s,e,w = map(int,input().split())
        graph[s].append((e,w))
    mn=bfs(0,n)
    print(f"#{tc} {mn}")



# import heapq
# from collections import deque
# def bfs(st):

#     q = deque([(st)])
#     v = [0]+[1e9]*(n)
#     while q:
#         c= q.popleft()
#         for e,w in graph[c]:
#             if v[e]>v[c]+w:
#                 v[e]=v[c]+w
#                 q.append(e)
#     return v[-1]


# for tc in range(1,int(input())+1):

#     n,E = map(int,input().split())

#     graph = [[] for _ in range(n+1)]
#     for _ in range(E):
#         s,e,w = map(int,input().split())
#         graph[s].append((e,w))
#     mn=bfs(0,n)
#     print(f"#{tc} {mn}")
    
from collections import deque
def bfs(st,goal):

    q = deque([(st,0)])
    mn = 1e9
    while q:
        c ,cnt= q.popleft()
        for e,w in graph[c]:
            if mn > w+cnt:
                q.append((e,w+cnt))
                if e==goal:
                    mn = w+cnt

    return mn

for tc in range(1,int(input())+1):

    n,E = map(int,input().split())

    graph = [[] for _ in range(n+1)]
    for _ in range(E):
        s,e,w = map(int,input().split())
        graph[s].append((e,w))
    mn=bfs(0,n)
    print(f"#{tc} {mn}")