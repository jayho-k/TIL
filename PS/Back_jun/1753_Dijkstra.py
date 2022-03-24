'''
다익 스트라 순서
1. 출발노드
2. 테이블 초기화
3. 그래프 만들기

함수 다익스트라
1. 우선순위 큐 생성 (heapq로 만듦)
    우선순위 큐에 저장해야 할 것들
    (거리, 위치(노드))
    테이블 초기 설정

2. while q 생성
    나온 거리(d)과 테이블에 있는 값을 비교
    if d < dist[p]:
        for 문 돌림
        인접한 노드 확인하고
        총 거리 = d + 새로운 거리

        if 총거리 < 테이블에 있는 거리:
            그럼 갱신해주셈
            그리고 코스트랑 노드번호 넣어 주셈

5 6
1
5 1 1
1 2 2
1 3 3
2 3 4
2 4 5
3 4 6
'''
import heapq
import sys

def dst(st):

    q = []
    heapq.heappush(q, (0,st))
    table[st] = 0
    
    while q:
        d, nw = heapq.heappop(q)

        # 방문처리 안한 곳 갈것임 => 테이블 값보다 작거나 같을 경우
        if d <= table[nw]:
            
            for dd, nxt in graph[nw]:
                nd = d + dd

                # 새로운게 더 작다면?
                if table[nxt] > nd:
                    table[nxt] = nd
                    heapq.heappush(q,(nd,nxt))


input = sys.stdin.readline
inf = 1e9
v, e = map(int,input().split())
st = int(input())

graph = [[] for _ in range(v+1)]

table = [inf]*(v+1)

# 그래프 생성
for i in range(e):
    s, f, c = map(int,input().split())
    graph[s].append((c,f))
    
dst(st)

for i in table[1:]:
    if i == inf:
        print('INF')
    else:
        print(i)



