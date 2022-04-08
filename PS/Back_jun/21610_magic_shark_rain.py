'''

1. padding()==> n으로 만들면 + 

문제
1. d방향으로 s칸 이동
2. 1채움
3. 구름 사라짐
4. 대각선으로 물복사(경계안으로)
5. 


1번 행(y)과 N번 행을 연결했고, 1번 열(x)과 N번 열도 연결했다. 
즉, N번 행의 아래에는 1번 행이, 1번 행의 위에는 N번 행이 있고, 1번 열의 왼쪽에는 N번 열이, N번 열의 오른쪽에는 1번 열이 있다.

(N, 1), (N, 2), (N-1, 1), (N-1, 2) 비구릉
바구니에 저장된 물의 양이 2 이상인 모든 칸에 구름이 생기고, 물의 양이 2 줄어든다. 이때 구름이 생기는 칸은 3에서 구름이 사라진 칸이 아니어야 한다.
 ←, ↖, ↑, ↗, →, ↘, ↓, ↙ 

범위로 넘어가면 다음자리로 넘겨줌
'''
from collections import deque
n,m = map(int, input().split())
grid = [list(map(int,input().split())) for _ in range(n)]

dy = [0,0,-1,-1,-1,0,1,1,1]
dx = [0,-1,-1,0,1,1,1,0,-1]

dy2 = [-1,1,1,-1] 
dx2 = [1,1,-1,-1]
move = [list(map(int, input().split())) for _ in range(m)]

c = deque([(n-1,0),(n-1,1),(n-2,0),(n-2,1)])
for d,s in move:

    nc = []

    while c:
        cy, cx = c.popleft()
        ncy = (cy+dy[d]*(s)+n)%n
        ncx = (cx+dx[d]*(s)+n)%n

        grid[ncy][ncx] += 1.0
        nc.append((ncy,ncx))
    
    #대각선 세기
    for ny, nx in nc:
        cnt = 0
        for dd in range(4):
            ny2 = ny + dy2[dd]
            nx2 = nx + dx2[dd]
            if 0<=ny2<n and 0<=nx2<n and grid[ny2][nx2] != 0:
                cnt += 1

        grid[ny][nx] += cnt


    for y in range(n):
        for x in range(n):
            if type(grid[y][x]) == int and grid[y][x] >=2:
                grid[y][x] -= 2
                c.append((y,x))

            elif type(grid[y][x]) == float:
                grid[y][x] = int(grid[y][x])

total = 0
for i in grid:
    total += sum(i)

print(total)






        # if 0<=ncy<n and 0<=ncx<n:
        #     grid[ncy][ncx] += 1.0

        # else:
        #     # 다음으로 넘겨줘야함
        #     ncy %= n
        #     ncx %= n
        #     grid[ncy][ncx] += 1.0

        #     print(c)



    # for y in range(n):
    #     for x in range(n):
    #         if type(grid[y][x]) == float:
    #             grid[y][x] = int(grid[y][x])
            

            




