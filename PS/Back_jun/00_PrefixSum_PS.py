'''
50 4 5 1
24 15 27 43
3 4 6 20 25
3 52

5 1 1 1
3
3
3 7



'''
# 20438_출석체크
import sys
input = sys.stdin.readline
n,k,q,m = map(int,input().split())
sleep = set(list(map(int,input().split())))
code = list(map(int,input().split()))
stud = [0]*(n+3)
n_stud = [0]*(n+3)
flag = False
for i in range(len(code)):
    if code[i] not in sleep:
        for c in range(0,len(stud),code[i]):
            if c not in sleep:
                stud[c]=1
                flag=True
# print(stud)
tmp = 0
for s in range(3,len(stud)):
    if stud[s]==0:
        tmp+=1
    n_stud[s] = tmp
# print(n_stud)
for _ in range(m):
    s,e = map(int,input().split())
    if flag:
        print(n_stud[e]-n_stud[s])
    else:
        print(n_stud[e]-n_stud[s]+1)



# # # 2167_2차원 배열의 합
# n,m = map(int,input().split())
# grid = [list(map(int,input().split())) for _ in range(n)]
# dp = [[0]*(m+1) for _ in range(n+1)]

# for y in range(1,n+1):
#     for x in range(1,m+1):
#         dp[y][x] = grid[y-1][x-1]+dp[y-1][x]+dp[y][x-1]-dp[y-1][x-1]

# k = int(input())
# for _ in range(k):
#     y1,x1,y2,x2 = map(int,input().split())
#     print(dp[y2][x2]-dp[y1-1][x2]-dp[y2][x1-1]+dp[y1-1][x1-1])
    