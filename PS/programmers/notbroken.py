'''
구간합
[[5,5,5,5,5],[5,5,5,5,5],[5,5,5,5,5],[5,5,5,5,5]]
[[1,0,0,3,4,4],[1,2,0,2,3,2],[2,1,0,3,1,2],[1,0,1,3,3,1]]
10

[[1,2,3],[4,5,6],[7,8,9]]
[[1,1,1,2,2,4],[1,0,0,1,1,2],[2,2,0,2,0,100]]
6
'''
# def solution(board, skill):
#     answer = 0
#     return answer
from pprint import pprint
# board = [[1,2,3],[4,5,6],[7,8,9]]
# skill = [[1,1,1,2,2,4],[1,0,0,1,1,2],[2,2,0,2,0,100]]


board = [[5,5,5,5,5],[5,5,5,5,5],[5,5,5,5,5],[5,5,5,5,5]]
skill = [[1,0,0,3,4,4],[1,2,0,2,3,2],[2,1,0,3,1,2],[1,0,1,3,3,1]]
n = len(board)
m = len(board[0])
# v = [0]*(m+1)*n
# v = [[0]*(m+1) for _ in range(n)]
v = [[0]*(m+1) for _ in range(n+1)]

for a,y1,x1,y2,x2,pwr in skill:

    if a == 1:
        v[y1][x1] -= pwr
        v[y1][x2+1] += pwr
        v[y2+1][x1] += pwr
        v[y2+1][x2+1] -= pwr

    else:
        v[y1][x1] += pwr
        v[y1][x2+1] -= pwr
        v[y2+1][x1] -= pwr
        v[y2+1][x2+1] += pwr

# 행 기준
for y in range(n):
    for x in range(m):
        v[y][x+1] += v[y][x]

# 열 기준
for x in range(m):
    for y in range(n):
        v[y+1][x] += v[y][x]

ans = 0
for y in range(n):
    for x in range(m):
        board[y][x] += v[y][x]
        if board[y][x] > 0:
            ans += 1

print(ans)





# for a,y1,x1,y2,x2,pwr in skill:

#     if a == 1:
#         for k in range(y2-y1+1):
#             v[y1+k][x1] -= pwr
#             v[y1+k][x2+1] += pwr
            
#     else:
#         for k in range(y2-y1+1):
#             v[y1+k][x1] += pwr
#             v[y1+k][x2+1] -= pwr
    
# total = 0
# cnt = 0
# for y in range(n):
#     for x in range(m+1):
#         total += v[y][x]
#         v[y][x] = total

#         if 0<=y<n and 0<= x<m:
#             board[y][x] += total
#             if board[y][x] > 0:
#                 cnt +=1

# print(v)
# print(board)
# print(cnt)





# pprint(board)



    # print(v)
    # for i in range(n):
    #     print(v[i*(m+1):i*(m+1)+(m+1)])
    # print('*'*30)



            # v[x1+(k*(m+1))] = - pwr
            # v[x1+(k*(m+1))+x2+1] = pwr
         # v[x1+(k*(m+1))] = pwr
            # v[x1+(k*(m+1))+x2+1] = -pwr