'''
비용, 늘어나는 고객의 수

12 2
3 5
1 1

10 3
3 1
2 2
1 3


'''
from pprint import pprint

def init():
    cost_custom_lst = [(0,0)]

    mx_cost = 0
    for _ in range(n):
        t_cost,t_custom = map(int,input().split())
        mx_cost = max(mx_cost,t_custom)
        cost_custom_lst.append((t_cost, t_custom))

    return mx_cost, cost_custom_lst


def init_dp_table():
    
    dp_table = [[0]*(c+mx_cost+1) for _ in range(n+1)]
    
    for i in range(c+mx_cost+1):
        dp_table[0][i] = INF
    
    return dp_table

def fill_dp_table():

    for y in range(1,n+1):
        cost, customer = cost_custom_lst[y]

        # x = 고객 수
        for x in range(1,c+mx_cost+1):
            if x <= customer:
                dp_table[y][x] = min(dp_table[y-1][x], cost)

            else:
                dp_table[y][x] = min(dp_table[y-1][x], dp_table[y][x-customer]+cost)

# [main]
# init
INF = 1e9
c,n = map(int,input().split())
mx_cost, cost_custom_lst = init()
dp_table = init_dp_table()

# play
fill_dp_table()

# ans
ans = 1e9
for i in range(c,c+mx_cost+1):
    ans = min(ans, dp_table[n][i])

# print answer
print(ans)









# from pprint import pprint

# c,n = map(int,input().split())

# mxPerson = 0
# lst = [[0,0]]
# for _ in range(n):
#     cost, person = map(int,input().split())
#     mxPerson = max(person,mxPerson)
#     lst.append([cost,person])

# dpTable = [[1e9]*(c+mxPerson+1) for _ in range(n+1)]

# ans = 1e9
# for y in range(1,n+1):
#     for x in range(1,c+mxPerson+1):
#         cost, person = lst[y][0], lst[y][1]
#         if x-person <= 0:
#             dpTable[y][x] =min(dpTable[y-1][x], cost)
#         else:
#             dpTable[y][x] =min(dpTable[y-1][x], dpTable[y][x-person]+cost)

#         if c <= x:
#             ans = min(dpTable[y][x],ans)

# print(ans)







# c, n = map(int,input().split())

# # 비용, 늘어나는 고객의 수
# lst = [list(map(int,input().split())) for _ in range(n)]
# table = [1e9]*(101+c)


# ans = 1e9
# for cost,cus in lst:

#     table[cus] = cost
#     for i in range(0,101+c):
#         table[i] = min(table[i], table[i-cus]+cost)

#         if c <= i:
#             ans = min(table[i],ans)

#     print(table[:c+5])


# # print(table)
# # print(table[c])
# print(ans)
