'''
2


1
5 2
1 3 3 6 7
8 13 9 12 8
4 16 11 12 6
2 4 1 23 2
9 13 4 7 3

6 3
29 21 26 9 5 8
21 19 8 0 21 19
9 24 2 11 4 24
19 29 1 0 21 19
10 29 6 18 4 3
29 11 15 3 3 29

'''

# def mx_count_flies(grid):
#     mx = 0
#     for y in range(n-k+1):
#         for x in range(n-k+1):
#             flies = 0
#             for yy in range(y,y+k):
#                 for xx in range(x,x+k):
#                     flies+=grid[yy][xx]
#             mx = max(mx,flies)
#     return mx
# for tc in range(1,int(input())+1):
#     n,k = map(int,input().split())
#     grid = [list(map(int,input().split())) for _ in range(n)]
#     ans = mx_count_flies(grid)
#     print(f"#{tc} {ans}")


def make_dp_table(grid):
    dp_table = [[0]*(n+1) for _ in range(n+1)]
    for y in range(1,n+1):
        for x in range(1,n+1):
            dp_table[y][x] = dp_table[y-1][x]+dp_table[y][x-1]+grid[y-1][x-1]-dp_table[y-1][x-1]
    return dp_table

def find_mx(k,dp):
    mx = 0
    for y in range(k,n+1):
        for x in range(k,n+1):
            com = dp[y][x]-dp[y-k][x]-dp[y][x-k]+dp[y-k][x-k]
            mx = max(mx, com)          
    return mx
for tc in range(1,int(input())+1):
    n,k = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]
    dp = make_dp_table(grid)
    mx = find_mx(k,dp)
    print(f"#{tc} {mx}")















