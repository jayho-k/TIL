
"""
3 310
50 40
100 70
200 150

1 5
1 10

"""

# x축을 score로 두고 풀어본 코드
n,m = map(int,input().split())
time_score = [(0,0)]

sum_score = 0
for i in range(n):
    t,s = map(int,input().split())
    time_score.append((t,s))
    sum_score += s

INF = 10001

dp = [[INF]*(sum_score+1) for _ in range(n+1)]

res = 0
for y in range(1,n+1):
    time,score = time_score[y]

    for x in range(1,sum_score+1):
        if x <= score:
            dp[y][x] = min(dp[y-1][x], time)
        else:
            dp[y][x] = min(dp[y-1][x], dp[y-1][x-score]+time)

        #최대 투자할 수 있는시간
        if dp[y][x] <= m:
            res = max(res,x)

# print(dp)
print(res)


# x축을 time으로 두고 풀어본 코드
n,m = map(int,input().split())
time_score = [(0,0)]+[tuple(map(int,input().split())) for _ in range(n)]

dp = [[0]*(m+1) for _ in range(n+1)]

for y in range(1,n+1):
    time,score = time_score[y]
    for x in range(1,m+1):
        if x < time:
            dp[y][x] = dp[y-1][x]
            continue
        dp[y][x] = max(dp[y-1][x],dp[y-1][x-time]+score)

print(dp[n][m])