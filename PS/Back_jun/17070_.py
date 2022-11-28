'''

6
0 0 0 0 0 0
0 1 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0

가로 세로 대각선을 판단해줘야함

'''

def dfs(d,pipe):
    global ans
    # print(pipe)
    pprint(visited)
    if pipe[1][0]==n-1 and pipe[1][1]==n-1:
        print(d)
        ans += d
        return

    if pipe[1][0]==n-1 or pipe[1][1]==n-1:

        return
    dly = pipe[1][0] - pipe[0][0]
    dlx = pipe[1][1] - pipe[0][1]

    # 가로
    if dly == 0 and dlx != 0:
        for tmp in [[(1,0)],[(0,1),(1,0),(1,1)]]:
            if len(tmp) == 1:
                ny = pipe[1][0] + tmp[0][0]
                nx = pipe[1][1] + tmp[0][1]
                if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
                    visited[ny][nx] = 1
                    dfs(d+1, [(pipe[1][0],pipe[1][1]),(ny,nx)])
                    visited[ny][nx] = 0

            else:
                t_cnt = 0
                for t in tmp:
                    ny = pipe[1][0] + t[0]
                    nx = pipe[1][1] + t[1]
                    if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
                        t_cnt += 1
                if t_cnt == 3:
                    visited[ny][nx] = 1
                    dfs(d+1, [(pipe[1][0],pipe[1][1]),(ny,nx)])
                    visited[ny][nx] = 0

    # 세로
    elif dly != 0 and dlx == 0:
        for tmp in [[(1,0)],[(0,1),(1,0),(1,1)]]:
            if len(tmp) == 1:
                ny = pipe[1][0] + tmp[0][0]
                nx = pipe[1][1] + tmp[0][1]
                if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
                    visited[ny][nx] = 1
                    dfs(d+1, [(pipe[1][0],pipe[1][1]),(ny,nx)])
                    visited[ny][nx] = 0
            else:
                
                t_cnt = 0
                for t in tmp:
                    ny = pipe[1][0] + t[0]
                    nx = pipe[1][1] + t[1]
                    if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
                        t_cnt += 1
                if t_cnt == 3:
                    visited[ny][nx] = 1
                    dfs(d+1, [(pipe[1][0],pipe[1][1]),(ny,nx)])
                    visited[ny][nx] = 0

    # 대각선
    else:
        for tmp in [[(1,0)],[(0,1),(1,0),(1,1)]]:
            if len(tmp) == 1:
                ny = pipe[1][0] + tmp[0][0]
                nx = pipe[1][1] + tmp[0][1]
                if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
                    visited[ny][nx] = 1
                    dfs(d+1, [(pipe[1][0],pipe[1][1]),(ny,nx)])
                    visited[ny][nx] = 0

            else:
                t_cnt = 0
                for t in tmp:
                    ny = pipe[1][0] + t[0]
                    nx = pipe[1][1] + t[1]
                    if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
                        t_cnt += 1
                if t_cnt == 3:
                    visited[ny][nx] = 1
                    dfs(d+1, [(pipe[1][0],pipe[1][1]),(ny,nx)])
                    visited[ny][nx] = 0

from pprint import pprint
n = int(input())
grid = [ list(map(int,input().split())) for _ in range(n)]
st = [(0,0),(0,1)]
visited = [[0]*n for _ in range(n)]
ans = 0
dfs(0,[(0,0),(0,1)])
print(ans)