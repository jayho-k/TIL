
"""
3 10
1
2
5
"""
# memory 4MB에서 메모리 초과가 뜬다.
from pprint import pprint

n,k = map(int,input().split())
conins = [int(input()) for _ in range(n)]

dpTable = [0]*(k+1)
dpTable[0] = 1

# x : 현재 가지고 있는 경우의 수
for coin in conins:
    for x in range(k+1):
        if x < coin:
            continue
        dpTable[x] = dpTable[x-coin] + dpTable[x]

print(dpTable[k])




# memory 4MB에서 메모리 초과가 뜬다.
# 그래서 테이블을 2차원에서 1차원으로 줄인거 같음 => 위에 1차원으로 줄인 방법
from pprint import pprint

n,k = map(int,input().split())
conins = [0]+[int(input()) for _ in range(n)]

dpTable = [[0]*(k+1) for _ in range(n+1)]
dpTable[0][0] = 1

# x : 현재 가지고 있는 경우의 수
for y in range(1,n+1):
    for x in range(k+1):
        coin = conins[y]
        if x < coin:
            dpTable[y][x] = dpTable[y-1][x]
            continue
        dpTable[y][x] = dpTable[y][x-coin] + dpTable[y-1][x]

print(dpTable[n][k])


















# n,knum = map(int,input().split())
# lst = [int(input()) for _ in range(n)]

# dp = [0]*(10001)
# dp[0] = 1

# for l in lst:
#     for k in range(1,knum+1):
        
#         if l<=k:
#             dp[k] = dp[k-l]+dp[k]

# print(dp)

# print(dp[knum])