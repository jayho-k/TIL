
"""
5 60
30 10 20 35 40
3 0 3 5 4
"""
from pprint import pprint

n,m = map(int,input().split())

memory_map = list(map(int,input().split()))
cost_map = list(map(int,input().split()))

memory_cost = [(0,0)]
sum_cost = 0
res = 0
for i in range(n):
    memory_cost.append((memory_map[i], cost_map[i]))
    sum_cost += cost_map[i]
    res += cost_map[i]

dp_table = [[0]*(sum_cost+1) for _ in range(n+1)]

for y in range(1,n+1):
    memory, cost = memory_cost[y]

    for x in range(sum_cost+1):
        if x < cost:
            dp_table[y][x] = dp_table[y-1][x]
        else:
            dp_table[y][x] = max(dp_table[y-1][x], dp_table[y-1][x-cost] + memory)

        if dp_table[y][x] >= m:
            res = min(res,x)

#pprint(dp_table)
print(res)
# if m !=0:
#     print(res)
# else:
#     print(0)