from pprint import pprint
import sys
input = sys.stdin.readline

def make_dp():

    for y in range(1,n+1):
        for x in range(1,m+1):
            # grid값 but, 1차원씩 작아서 -1를 해준다. + dp 위쪽 + dp 왼쪽 - dp의 대각선 
            # 
            dp[y][x] = grid[y-1][x-1] + dp[y-1][x] + dp[y][x-1] - dp[y-1][x-1]



n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dp = [[0]*(m+1) for _ in range(n+1)]
