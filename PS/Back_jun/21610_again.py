'''
5 4
0 0 1 0 2
2 3 2 1 0
4 3 2 9 0
1 0 2 9 0
8 8 2 1 0
1 3
3 4
8 1
4 8

1. 시작점
2. 이동
3. 뿌려주기
4. check
5. 구름 생성 찾기

(N-1,0), (N-1,1), (N-2,0), (N-2,1)


'''

def move(d,s,clud_lst):

    # new_grid = [[0]*n for _ in range(n)]
    n_clud_lst = []
    for i in range(len(clud_lst)):
        y,x = clud_lst[i]
        ny = (y+(dy[d]*s)%n)%n
        nx = (x+(dx[d]*s)%n)%n
        n_clud_lst.append((ny,nx))
    return n_clud_lst

def add_water(clud_lst,grid):

    # n_grid = [[0]*n for _ in range(n)]
    for i in range(len(clud_lst)):
        y,x = clud_lst[i]
        grid[y][x] += 1

    return grid

def copy_skill(grid,clud_lst):

    skilled = []
    for i in range(len(clud_lst)):
        y,x = clud_lst[i]
        cnt = 0
        for d in (2,4,6,8):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and grid[ny][nx]!=0:
                cnt += 1
        skilled.append((y,x,cnt))

    for sky,skx,sk_cnt in skilled:
        grid[sky][skx] += sk_cnt

    return grid

def create_clud(grid,clud_lst):

    n_clud_lst = []
    n_grid = [[0]*n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            if grid[y][x] >=2 and (y,x) not in clud_lst:
                n_grid[y][x] = grid[y][x]-2
                n_clud_lst.append((y,x))
            else:
                n_grid[y][x] = grid[y][x]

    return n_grid,n_clud_lst


from pprint import pprint
import sys
input = sys.stdin.readline

n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
magic = [tuple(map(int,input().split())) for _ in range(m)]
dy = [0,0,-1,-1,-1,0,1,1,1]
dx = [0,-1,-1,0,1,1,1,0,-1]
stp = [(n-1,0),(n-1,1),(n-2,0),(n-2,1)]

for d,s in magic:
    clud_lst = move(d,s,stp)
    n_grid = add_water(clud_lst,grid)
    n_grid = copy_skill(n_grid,clud_lst)
    grid,stp = create_clud(n_grid,clud_lst)



total = 0
for i in range(n):
    for j in range(n):
        total += grid[i][j]

print(total)

