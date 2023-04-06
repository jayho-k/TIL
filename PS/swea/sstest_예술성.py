"""

5
1 2 2 3 3
2 2 2 3 3
2 2 1 3 1
2 2 1 1 1
2 2 1 1 1

"""
from pprint import pprint
from collections import deque,defaultdict

def count_lines(y,x):

    visited[y][x]=1
    q = deque([(y,x)])
    dif_cnt = defaultdict(int)

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0:
                if group_grid[y][x]==group_grid[ny][nx]:
                    visited[ny][nx]=1
                    q.append((ny,nx))

                elif group_grid[y][x]!=group_grid[ny][nx]:
                    dif_cnt[group_grid[ny][nx]]+=1
    return dif_cnt

def make_group_bfs(y,x,g_num):

    q = deque([(y,x)])
    same_cnt = 1
    same_num = grid[y][x]
    group_grid[y][x]=g_num

    while q:
        y,x = q.popleft()
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and group_grid[ny][nx]==0:
                if grid[y][x]==grid[ny][nx]:
                    same_cnt+=1
                    group_grid[ny][nx]=g_num
                    q.append((ny,nx))

    return same_cnt,same_num

def make_diff():

    for y in range(n):
        for x in range(n):
            if visited[y][x]==0:
                dif_cnt = count_lines(y,x)
                diff_groups[group_grid[y][x]]=dif_cnt
    # pprint(diff_groups)


def make_group():
    g_num = 1

    for y in range(n):
        for x in range(n):
            if group_grid[y][x] == 0:
                same_cnt,same_num = make_group_bfs(y, x, g_num)
                same_groups[g_num]=(same_cnt,same_num)
                g_num += 1
    # pprint(same_groups)
def hal_cal():
    total = 0
    for h1 in diff_groups:
        for h2 in diff_groups[h1]:
             total += (same_groups[h1][0] + same_groups[h2][0]) \
                  * same_groups[h1][1] \
                  * same_groups[h2][1] \
                  * diff_groups[h1][h2]
    return total

def r_p90():
    # 주의
    # 위에 부분은 띄어서 감
    # 밑에 부분은 연속으로 i 같은 것을 더하지 않고 간다.
    # 기준점을 잡아주었기 때문에 크기만 더하면 된다는 것을 잊지 말자

    n_grid = [[0]*n for _ in range(n)]
    y,x = n//2,n//2
    n_grid[y][x]=grid[y][x]
    for i in range(1,n//2+1):
        for d in range(4):
            ny = y+dy[d]*i
            nx = x+dx[d]*i
            n_grid[ny][nx] = grid[nx][n-1-ny]

    return n_grid

def r_m90(n_grid):
    m = n//2
    for y in range(0,n,(n//2)+1):
        for x in range(0,n,(n//2)+1):
            for i in range(n//2):
                for j in range(n//2):
                    n_grid[y+j][x+m-i-1] = grid[y+i][x+j]

    return n_grid




n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]
ans = 0
for _ in range(4):
    group_grid = [[0]*n for _ in range(n)]
    visited = [[0] * n for _ in range(n)]
    same_groups = {}
    diff_groups = {}

    # 그룹 만들기
    make_group()

    # 경계면 개수 세기
    make_diff()

    # 조화 점수 계산하기
    cal_res = hal_cal()
    ans += cal_res

    # 십자가 90도 회전
    n_grid = r_p90()

    # -90도 회전
    grid = r_m90(n_grid)
print(ans)


# # -90도 회전
# grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
# n_grid = [[0]*3 for _ in range(3)]
# for y in range(3):
#     for x in range(3):
#         n_grid[y][x] = grid[x][3-1-y]
# print(n_grid)

# # +90도 회전
# grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
# n_grid = [[0]*3 for _ in range(3)]
# for y in range(3):
#     for x in range(3):
#         n_grid[y][3-1-x] = grid[x][y]
# print(n_grid)

