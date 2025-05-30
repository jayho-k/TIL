'''
4 7
6 13
4 8
3 6
5 12


table[i][j] = max(table[i-1][j], v+table[i-1][j-w])


v+table[i-1][j-w] :
v = 지금 물건의 가치
i-1 = 위에
j-w => 내가 하나 더 들수 있는지(그중 최대 가치) 
==> 그가치 + 지금 가치 = v+table[i-1][j-w]

table[i-1][j]: 그 무게일때 최대 가치
그 무게와 더 넣을 수 있는 것과 비교 ==> 큰걸 고름

1535 , 4781 , 7579
'''

from pprint import pprint

n,k = map(int,input().split())

bag = [[0,0]] + [list(map(int,input().split())) for _ in range(n)]
dpTable = [[0]*(k+1) for _ in range(n+1)]


for y in range(1,n+1):
    for x in range(1,k+1):
        w,v = bag[y]
        if x < w:
            dpTable[y][x] = dpTable[y-1][x]
        else:
            dpTable[y][x] = max(dpTable[y-1][x], dpTable[y-1][x-w]+v)

pprint(dpTable[n][k])



# n,k = map(int,input().split())
# bag = [[0,0]] + [list(map(int,input().split())) for _ in range(n)]
# dpTable = [0]*(k+1)

# for y in range(1,n+1):
#     tmpDpTable = [0]*(k+1)
#     for x in range(1,k+1):
#         w,v = bag[y][0], bag[y][1]
#         if x < w:
#             tmpDpTable[x] = dpTable[x]
#         else:
#             tmpDpTable[x] = max(dpTable[x-w]+v, dpTable[x])

#     dpTable = tmpDpTable

# print(dpTable[k])


# from pprint import pprint

# n,k = map(int,input().split())

# bag = [[0,0]] + [list(map(int,input().split())) for _ in range(n)]
# dpTable = [[0]*(k+1) for _ in range(n+1)]

# for y in range(1,n+1):
#     for x in range(1,k+1):
#         w,v = bag[y][0], bag[y][1]
#         if x < w:
#             dpTable[y][x] = dpTable[y-1][x]

#         else:
#             dpTable[y][x] = max(dpTable[y-1][x-w]+v, dpTable[y-1][x])

# #pprint(dpTable)
# print(dpTable[n][k])







# from pprint import pprint

# n,k = map(int,input().split())

# # w,v
# items = [[0,0]]+[list(map(int,input().split())) for _ in range(n)]
# table = [[0]*(k+1) for _ in range(n+1)]

# for i in range(1,n+1):
#     for j in range(1,k+1):
#         w = items[i][0]
#         v = items[i][1]
    
#         if j < w:
#             table[i][j] = table[i-1][j]

#         else:
#             table[i][j] = max(table[i-1][j], v+table[i-1][j-w])

# pprint(table)
# print(table[n][k])





# # 반례 
# # 1 2
# # 1 3

# n,k = map(int,input().split())

# # w,v
# items = [[0,0]]+[list(map(int,input().split())) for _ in range(n)]
# # table = [[0]*(k+1) for _ in range(n+1)]
# table = [0]*(k+1)

# for w,v in items:
#     for j in range(1,k+1):

#         if j < w:
#             table[j] = table[j]

#         else:
#             table[j] = max(table[j], v+table[j-w])

#     print(table)
# print(table[k])
