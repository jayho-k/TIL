'''

5
5
0 0 0 1 0
0 1 0 1 0
0 0 1 0 2
1 0 1 1 0
0 0 1 0 0
6
1 0 1 0 1 0
0 0 2 0 0 0
1 1 0 1 1 0
0 1 0 1 1 0
0 0 0 0 0 0
0 1 0 1 0 1
7
0 0 0 0 0 0 1
1 1 1 1 1 0 1
0 0 0 0 0 0 1
0 1 1 1 1 1 1
0 0 0 0 0 2 1
1 1 0 1 1 0 1
0 0 0 0 0 0 1
8
0 0 0 0 1 1 1 1
1 0 1 0 1 1 1 1
1 0 0 0 2 0 0 0
1 0 1 1 0 1 1 0
1 0 1 1 0 1 1 0
1 0 1 1 0 0 0 0
1 0 1 1 1 1 1 0
1 0 1 1 1 1 1 0
8
0 0 1 1 1 0 0 0
1 0 0 1 0 0 1 1
1 1 0 0 0 1 1 1
1 0 0 1 1 0 1 0
0 0 1 0 0 2 1 0
0 1 0 0 1 0 1 0
0 1 0 1 0 0 0 1
0 0 1 0 0 1 0 1

range(1, n+1)
'''
from pprint import pprint

def st(lsts):
    for y in range(n):
        for x in range(n):
            if lsts[y][x] ==2:
                return y, x

T = int(input())
# T = 1
for tc in range(1,T+1):
    n = int(input())
    lsts = [list(map(int, input().split())) for _ in range(n)]

    sty, stx = st(lsts)
    # 동서남북
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]
    # di = 0 # 방향 #방향을 바꿔줄 필요가 없기 때문에 굳이 사용안해도 될듯?

    for d in range(4):
        for k in range(1,n+1): # 혹시모르니 +1하자 //
            ny = sty + dy[d]*k
            nx = stx + dx[d]*k

            if 0<= ny < n and 0<= nx < n:
                if lsts[ny][nx] == 1:
                    break
                lsts[ny][nx] = 3

    # pprint(lsts)
    ans = 0
    for l in lsts:
        ans += l.count(0)

    print(f'#{tc} {ans}')
























