'''
90도
1. 좌우 반전
2. n-1-x
for y in range():
    for x in range():




'''
def bfs(sy,sx):

    global mx

    q = deque([(sy,sx)])
    visited[sy][sx] = 1
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    cnt = 1
    while q:
        y,x = q.popleft()

        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            if 0<=ny<n and 0<=nx<n and grid[ny][nx] != 0 and visited[ny][nx] ==0:
                visited[ny][nx] = 1
                q.append((ny,nx))
                cnt += 1

    if mx < cnt:
        mx = cnt


def sm(grid):
    total = 0
    for g in grid:
        total += sum(g)
    return total


from collections import deque
from pprint import pprint


N,Q = map(int,input().split())
n = 2**N
grid = [list(map(int,input().split())) for _ in range(n)]
L = list(map(int,input().split()))


dy = [0,0,1,-1]
dx = [1,-1,0,0]

for q in range(Q):
    l = L[q]
    # n = 2**N # 전체
    m = 2**l # 부분
    r_grid = [[0]*n for _ in range(n)]


    # 부분에서 가장 왼쪽 첫번째 값 찍기
    for y in range(0,n,m):
        for x in range(0,n,m):

            # 부분 부분 rotation진행 (다시 해보기)
            for y1 in range(m):
                for x1 in range(m):
                    r_grid[y+x1][x+m-1-y1] = grid[y+y1][x+x1]


    chck = []
    for y in range(n):
        for x in range(n):
            if r_grid[y][x] == 0:
                    continue
            cnt = 0
            for d in range(4):
                ny = y+dy[d]
                nx = x+dx[d]

                if ny<0 or ny>=n or nx<0 or nx>=n:
                    continue

                elif r_grid[ny][nx] > 0:
                    cnt += 1

            if cnt < 3:
                chck.append((y,x))

    for cy,cx in chck:
        r_grid[cy][cx] -= 1

    grid = r_grid


mx = 0
visited = [[0]*n for _ in range(n)]
for i in range(n):
    for j in range(n):
        if visited[i][j] ==0 and grid[i][j] !=0:
            bfs(i,j)

total = sm(grid)
print(total)
print(mx)












































# n,Q = map(int,input().split())
# grid = [list(map(int,input().split())) for _ in range((n**2)-1)]
# L = list(map(int,input().split()))

# dy = [0,0,1,-1]
# dx = [1,-1,0,0]

# for q in range(Q):
#     l = L[q]
#     full = 2**n
#     part = 2**l
#     prt = div(grid, n, l)

#     # 부분을 하나씩 뽑아서 rotation
#     n_prt = []
#     for p in prt:
#         nw_p = rot(p)
#         n_prt.append(nw_p)
#     l_tmp = list(map(list,zip(*n_prt)))


#     # 여기부터
#     n_ful = []
#     for lt in l_tmp:
#         k = 0
#         for _ in range(full//2):
#             tp = []
#             for f in range(k,full//2+k):
#                 tp += lt[f]
#             n_ful.append(tp)
#         k+=full//2


#     for y in range(full):
#         for x in range(full):
#             cnt = 0
#             for d in range(4):
#                 ny = y + dy[d]
#                 nx = x + dx[d]
#                 if 0<=ny<full and 0<nx<full and n_ful[ny][nx] == 0:
#                     cnt += 1
#             if cnt >=2:
#                 n_ful[y][x] -= 1


# pprint(n_ful)
            

