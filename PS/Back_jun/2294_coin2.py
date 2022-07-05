'''
3 15
1
5
12

'''
from pprint import pprint
n,knum = map(int,input().split())
lst = [int(input()) for _ in range(n)]


dp = [1e9]*(knum+1)
dp[0] = 0

# dp[1][0] = 1
# print(lst)
# pprint(dp)

for i in range(n):
    for k in range(1,knum+1):
        if lst[i]<=k:

            dp[k] = min(dp[k-lst[i]]+1, dp[k])

if dp[-1]==1e9:
    print(-1)

else:
    print(dp[-1])


















# dp = [[1e9]*(knum+1)]+[[0]*(knum+1) for _ in range(n)]
# dp[1][0] = 1
# print(lst)
# pprint(dp)

# for i in range(n):
#     for k in range(1,knum+1):
#         # if lst[i]<=knum:

#         dp[i][k] = min(dp[i-1][k], dp[i][k-lst[i]]+1)

# pprint(dp)


