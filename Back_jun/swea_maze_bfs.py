'''
도착까지 최소가 몇칸인지 알아봐야함

미로
1. 보드를 만들어 준다
2. visited에 값을 계속해서 더하면서 추가를 해준다

5
13101
10101
10101
10101
10021
'''

from collections import deque

def st_p(board, n):
    for i in range(n):
        for j in range(n):
            if board[i][j] == 2:
                sty, stx = i, j
            if board[i][j] == 3:
                gy, gx = i, j

    return sty, stx, gy, gx

def bfs(y, x):
    q = deque([])

    # 동서남북
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]
    q.append((y,x))
    cnt = 0

    while q:
        y, x = q.popleft()
        if board[y][x] == 3:
            return

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<n and board[ny][nx] != 1 and board[ny][nx] != 2 and board[ny][nx] < 10:
                board[ny][nx] = board[y][x] + 10
                q.append((ny,nx))

                # pprint(board)

T = int(input())
for tc in range(1, T+1):
    n = int(input())
    board = [list(map(int, input())) for _ in range(n)]

    sty, stx, gy, gx = st_p(board, n)
    bfs(sty, stx)
    g = board[gy][gx]

    if g == 3:
        print(f'#{tc} 0')

    else:
        print(f'#{tc} {(g-12)//10}')

    

