

n = int(input())

dp = [40]*(n+1)
dp[1] = 0

for i in range(1,n):
    for j in range(0,n+1,i):
        if j>=2:
            if i==j:
                dp[j] = min(i,dp[j])

            if j==i*2:
                dp[j] = min(dp[j], dp[j-i]+2)

            elif j > i*2:
                dp[j] = min(dp[j], dp[j-i]+1)

    print(dp)
for a in range(n-1,-1,-1):
    for b in range(1,a):
        if dp[a-b] > dp[a]+b:
            dp[a-b] = dp[a]+b

    print(dp)