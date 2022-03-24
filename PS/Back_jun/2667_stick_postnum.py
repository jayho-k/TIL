# '''
# grouping

# 7
# 1010100
# 0110101
# 1110101
# 0000111
# 0100000
# 0111110
# 0111000
# '''
from collections import deque
from pprint import pprint

def bfs(y,x):

    q = deque([(y,x)])
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]
    visited[y][x] = num

    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0 and grid[ny][nx] != 0:
                visited[ny][nx] = num
                q.append((ny,nx))

n = int(input())
grid = [list(map(int, input())) for _ in range(n)]
visited = [[0]*n for _ in range(n)]

num = 0
for y in range(n):
    for x in range(n):
        if not visited[y][x] and grid[y][x]:
            num += 1
            bfs(y,x)

ans_lst = []
for v in visited:
    ans_lst += v

ans = []
for i in range(1,num+1):
    ans.append(ans_lst.count(i))

ans.sort()
print(num)
for a in ans:
    print(a)