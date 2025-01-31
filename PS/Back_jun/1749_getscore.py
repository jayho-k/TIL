from pprint import pprint
import sys
input = sys.stdin.readline

def make_dp():

    for y in range(1,n+1):
        for x in range(1,m+1):
            # grid값 but, 1차원씩 작아서 -1를 해준다. + dp 위쪽 + dp 왼쪽 - dp의 대각선 
            dp[y][x] = grid[y-1][x-1] + dp[y-1][x] + dp[y][x-1] - dp[y-1][x-1]



n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dp = [[0]*(m+1) for _ in range(n+1)]
make_dp()

ans = -1e9
for dy in range(1,n+1):
    for dx in range(1,m+1):
        for y in range(dy,n+1):
            for x in range(dx,m+1):
                ans = max(ans, dp[y][x]-dp[dy-1][x]-dp[y][dx-1]+dp[dy-1][dx-1])
print(ans)