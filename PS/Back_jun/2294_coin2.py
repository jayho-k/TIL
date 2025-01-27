'''
3 15
1
5
12

'''
from pprint import pprint

def init_dp_table():
    dpTable = [[0]*(k+1) for _ in range(n+1)]

    for i in range(1,k+1):
        dpTable[0][i] = INF

    return dpTable


def fill_table():
    for y in range(1,n+1):
        coin = coins[y]
        for x in range(1,k+1):
            if x < coin:
                dpTable[y][x] = dpTable[y-1][x]
                continue
            # 뭐가 늘어나고 있는지 확인을 해야하는구나? 그냥 코인 하나씩 추가하는 거니깐 +1이 맞지
            dpTable[y][x] = min(dpTable[y][x-coin]+1, dpTable[y-1][x])


# input
n,k = map(int,input().split())
coins = [0]+[int(input()) for _ in range(n)]
INF = 1e9

# init
dpTable = init_dp_table()

# play 
fill_table()

# ans
if dpTable[n][k] == INF:
    print(-1)
else:
    print(dpTable[n][k])









# from pprint import pprint
# n,knum = map(int,input().split())
# lst = [int(input()) for _ in range(n)]


# dp = [1e9]*(knum+1)
# dp[0] = 0

# # dp[1][0] = 1
# # print(lst)
# # pprint(dp)

# for i in range(n):
#     for k in range(1,knum+1):
#         if lst[i]<=k:

#             dp[k] = min(dp[k-lst[i]]+1, dp[k])

# if dp[-1]==1e9:
#     print(-1)

# else:
#     print(dp[-1])


















# dp = [[1e9]*(knum+1)]+[[0]*(knum+1) for _ in range(n)]
# dp[1][0] = 1
# print(lst)
# pprint(dp)

# for i in range(n):
#     for k in range(1,knum+1):
#         # if lst[i]<=knum:

#         dp[i][k] = min(dp[i-1][k], dp[i][k-lst[i]]+1)

# pprint(dp)


