'''
비용, 늘어나는 고객의 수

10 3
3 1
2 2
1 3

'''
from pprint import pprint

c,n = map(int,input().split())

mxPerson = 0
lst = [[0,0]]
for _ in range(n):
    cost, person = map(int,input().split())
    mxPerson = max(person,mxPerson)
    lst.append([cost,person])

dpTable = [[1e9]*(c+mxPerson+1) for _ in range(n+1)]

ans = 1e9
for y in range(1,n+1):
    for x in range(1,c+mxPerson+1):
        cost, person = lst[y][0], lst[y][1]
        if x-person <= 0:
            dpTable[y][x] =min(dpTable[y-1][x], cost)
        else:
            dpTable[y][x] =min(dpTable[y-1][x], dpTable[y][x-person]+cost)

        if c <= x:
            ans = min(dpTable[y][x],ans)

print(ans)







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
