'''

5
1 4 1 3 1
'''
from pprint import pprint
def caculate(i,j,ai,aj):
    return (j-i)*(1+abs(ai-aj))
# lst = [-1,1 ,5 ,2 ,1 ,6]
# print(caculate(2,4,lst[2],lst[4]))

n = int(input())
lst = [-1]+list(map(int,input().split()))
dp = [[1e9]*(n+1) for _ in range(n+1)]
for fx in range(2,n+1):
    dp[1][fx] = caculate(1,fx,lst[1],lst[fx])


for y in range(2,n+1):
    for x in range(y+1,n+1):
        # print(caculate(y,x,lst[y],lst[x]))
        dp[y][x] = caculate(y,x,lst[y],lst[x])
        # dp[y][x] = min(caculate(y,x,lst[y],lst[x]),dp[y-1][x])

pprint(dp)
# print(dp[n-1][n])


# INF = 999999999
# n = int(input())
# A = list(map(int, input().split()))
# # dp[i]는 i까지 가는데 드는 최소 힘
# dp = [0] + [INF] * (n - 1)

# for i in range(1, n):
#     for j in range(0, i):
#         print((i - j) * (1 + abs(A[i] - A[j])), dp[j])
#         power = max((i - j) * (1 + abs(A[i] - A[j])), dp[j]) 
#         # print(dp[i], power)
#         dp[i] = min(dp[i], power)
#         print(dp)
#     print('*'*30)
# print(dp[-1])