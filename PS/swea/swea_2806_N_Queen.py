'''

5 4 2
1 2 3
1 2 6
2 3 2
3 4 4
3 5 3
5
4

6 9 2
2 3 1
1 2 1
1 3 3
2 4 4
2 5 5
3 4 3
3 6 2
4 5 4
4 6 3
5 6 7
5
6
'''
import heapq

def dsk(strt):

    q = []
    heapq.heappush(q,(0,strt))
    table[strt] = 0

    while q:
         = heapq.heappop(q)





# 교차로, 도로, 목적지 후보의 개수
n,m,t = map(int, input().split())

# g랑 h사이는 무조건 간다
s,g,h = map(int, input().split())

# 도로 m개의 a와 b사이에 길이 d의 양방향 도로가 있다

graph = [[] for _ in range(n+1)]

for _ in range(m):
    st, frm, cst = map(int, input().split())
    graph[st].append((cst,frm))
    graph[frm].append((cst,st))

inf = 1e9
table = [inf]*(n+1)

goals = [int(input()) for _ in range(t)]


