'''
2
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
import sys
input = sys.stdin.readline

def dsk(strt):

    table[strt] = 0
    q = []
    heapq.heappush(q,(0,strt))

    while q:
        d, nw = heapq.heappop(q)

        if d <= table[nw]:

            for dd, nxt in graph[nw]:
                nd = dd + d

                if nd <= table[nxt]:
                    table[nxt] = nd
                    heapq.heappush(q,(nd,nxt))

T = int(input())
for _ in range(T):
    # 교차로, 도로, 목적지 후보의 개수
    n,m,t = map(int, input().split())

    # g랑 h사이는 무조건 간다
    s,g,h = map(int, input().split())

    # 도로 m개의 a와 b사이에 길이 d의 양방향 도로가 있다
    graph = [[] for _ in range(n+1)]

    for _ in range(m):
        st, frm, cst = map(int, input().split())
        if (st == h and frm == g) or (st==g and frm==h):
            graph[st].append((float(cst),frm))
            graph[frm].append((float(cst),st))

        graph[st].append((cst,frm))
        graph[frm].append((cst,st))

    inf = 1e9
    table = [inf]*(n+1)

    goals = [int(input()) for _ in range(t)]

    dsk(s)

    ans = []
    for g in goals:
        if table[g] != inf and isinstance(table[g],float):
            ans.append(g)

    ans.sort()

    print(*ans)

import bisect
