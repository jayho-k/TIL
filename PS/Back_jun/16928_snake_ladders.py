'''



'''
def bfs(st):

    q = deque([st])

    while q:
        m,cnt = q.popleft()
        if m == 100:
            return cnt

        for i in range(1,7):
            new_m = m + i
            if new_m <= 100 and new_m not in dupl:
                dupl.add(new_m)
                if graph[new_m] == []:
                    q.append((new_m,cnt+1))
                    
                else:
                    q.append((graph[new_m][0],cnt+1))

from collections import deque
from sys import stdin
input = stdin.readline
n,m = map(int,input().split())
graph = [[] for _ in range(101)]
dupl = set()
for lx,ly in (map(int,input().split()) for _ in range(n)):
    graph[lx].append(ly)

for su,sv in (map(int,input().split()) for _ in range(m)):
    graph[su].append(sv)

print(bfs((1,0)))










# grid = []
# tmp = []
# for g in range(1,101):
#     tmp.append(g)
#     if not g%10:
#         grid.append(tmp)
#         tmp = []

