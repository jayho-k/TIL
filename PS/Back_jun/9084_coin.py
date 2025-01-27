
"""
3
2
1 2
1000
3
1 5 10
100
2
5 7
22


1
3
1 5 10
100

2
5 7
22
"""
from pprint import pprint



def init():

    dp_table = [[0]*(m+1) for _ in range(n+1)]
    dp_table[0][0] = 1

    return dp_table

def make_dp_table():
    for y in range(1,n+1):
        coin = coins[y]
        dp_table[y][0] = 1
        for x in range(1,m+1):
            if x < coin:
                dp_table[y][x] = dp_table[y-1][x]
                continue
            dp_table[y][x] = dp_table[y-1][x] + dp_table[y][x-coin]



T = int(input())
for _ in range(T):
    
    # input
    n = int(input())
    coins = [0]+list(map(int,input().split()))
    m = int(input())

    # init
    dp_table = init()

    # make dp table
    make_dp_table() # 1
    
    print(dp_table[n][m])
