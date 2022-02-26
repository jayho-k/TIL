'''
도착할 수 있는지 없는지

3
5
13101
10101
10101
10101
10021
5
10031
10111
10101
10101
12001
5
00013
01110
21000
01111
00000
0. 그래프 작성
1. 좌표 찍기 ==> 2가 출발점
2. 탐색 ==> 이동 ==> 어디로, 안에 있고, 방문이 안되어 있고// 재귀
3. 방문처리 ==> 1로 해줄것임
4. 재귀를 사용
5. 

'''
def st_p(n):
    for i in range(n):
        for j in range(n):
            if board[i][j] ==2:
                sty, stx = i, j
    return sty, stx

def dfs(y, x):
    global ans

    #동남서북
    dy = [0,1,0,-1]
    dx = [1,0,-1,0]

    for d in range(4):
        ny = y+dy[d]
        nx = x+dx[d]
        if 0<=nx<n and 0<=ny<n and board[ny][nx] != 1:
            if board[ny][nx] == 3:
                ans = 1
                return
            board[ny][nx] = 1
            dfs(ny, nx)
            
T = int(input())
for tc in range(1,T+1):
    n = int(input())
    board = [list(map(int, input())) for _ in range(n)]
    sty, stx = st_p(n)

    
    ans = 0
    dfs(sty, stx)
    print(f'#{tc} {ans}')