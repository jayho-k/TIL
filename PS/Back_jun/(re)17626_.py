'''

25


'''
n = int(input())
dp = [0]*(n+1)
dp[0] = 0
dp[1] = 1

for i in range(2,n+1):
    
    mn = 1e9
    j = 1
    while j**2<=i:
        mn = min(mn,dp[i-(j**2)])
        j+=1
    dp[i] = mn+1

print(dp[-1])