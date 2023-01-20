'''
20438_출석체크 반례
입력
50 4 5 2
24 15 27 43
3 4 6 20 25
3 25
26 52

정답
12
13

4 3
1 2 3 4
2 3 4 5
3 4 5 6
4 5 6 7
2 2 3 4
3 4 3 4
1 1 4 4

# 21318번
9
1 2 3 3 4 1 10 8 1
5
1 3
2 5
4 7
9 9
5 9

4 0
2 -2 2 -2


3 5
2 3 -21 -22 -23
5 6 -22 -23 -25
-22 -23 4 10 2
'''

# 1749_점수따먹기
from pprint import pprint
import sys
input = sys.stdin.readline

def make_dp():
    dp = [[0]*(m+1) for _ in range(n+1)]
    for y in range(1,n+1):
        for x in range(1,m+1):
            dp[y][x] = grid[y-1][x-1]+dp[y-1][x]+dp[y][x-1]-dp[y-1][x-1]
    return dp


n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dp = make_dp()
mx = -10001

for y1 in range(1,n+1):
    for x1 in range(1,m+1):
        for y2 in range(y1,n+1):
            for x2 in range(x1,m+1):
                mx = max(mx,(dp[y2][x2]-dp[y2][x1-1]-dp[y1-1][x2]+dp[y1-1][x1-1]))
print(mx)

# # 설명 필요
# mx = -10001
# # y의 범위를 정해준다
# for y1 in range(1,n+1):
#     p = [0]*(m+1)
#     for y2 in range(y1,n+1):
#         t = [0]*(m+1)
#         for i in range(1,m+1):

#             # y2줄에 누적합을 다 넣어 놓음
#             p[i] += dp[y2][i]

#             # y2줄에 누적합과 
#             t[i] = max(t[i-1]+p[i],p[i])
#             mx = max(t[i],mx)

 






# # 2015_수들의 합 4
# # 다시 생각해보기

# from collections import defaultdict
# import sys
# input = sys.stdin.readline

# n,k = map(int,input().split())
# arr = list(map(int,input().split()))
# dp = [0]
# store = {0:1}
# for i in range(n):
#     dp.append(dp[-1]+arr[i])

# ans = 0
# for j in range(1,n+1):

#     if dp[j]-k in store:
#         ans += store[dp[j]-k]

#     if dp[j] in store:
#         store[dp[j]] +=1
#     else:
#         store[dp[j]] =1

# print(ans)

# # 21318_피아노 체조
# import sys
# input = sys.stdin.readline
# def make_dp():
#     dp = [0]*(n)
#     for i in range(1,n):
#         if lst[i-1]>lst[i]:
#             dp[i]=dp[i-1]+1
#         else:
#             dp[i]=dp[i-1]
#     else:
#         dp = [0]+dp
#     return dp

# n = int(input())
# lst = list(map(int,input().split()))
# q = int(input())
# dp = make_dp()

# for _ in range(q):
#     x,y = map(int,input().split())
#     print(dp[y]-dp[x])


# #  구간 합 구하기 5
# from pprint import pprint
# import sys
# input = sys.stdin.readline
# def make_dp():
#     dp = [[0]*(n+1) for _ in range(n+1)]
#     for y in range(1,n+1):
#         for x in range(1,n+1):
#             dp[y][x] = grid[y-1][x-1]+dp[y-1][x]+dp[y][x-1]-dp[y-1][x-1]
#     return dp

# n,m = map(int,input().split())
# grid = [list(map(int,input().split())) for _ in range(n)]
# dp = make_dp()

# for _ in range(m):
#     y1,x1,y2,x2 = map(int,input().split())
#     print(dp[y2][x2]-dp[y1-1][x2]-dp[y2][x1-1]+dp[y1-1][x1-1])



# # 20438_출석체크
# import sys
# input = sys.stdin.readline
# n,k,q,m = map(int,input().split())
# sleep = set(list(map(int,input().split())))
# code = list(map(int,input().split()))
# stud = [0]*(n+3)

# for i in range(len(code)):
#     if code[i] in sleep:
#         continue
#     for c in range(code[i],len(stud),code[i]):
#         if c not in sleep:
#             stud[c]=1


# prefix = [stud[0]]
# for s in range(1,len(stud)):
#     prefix.append(prefix[-1]+stud[s])

# for _ in range(m):
#     s,e = map(int,input().split())
#     print(e-s+1-(prefix[e]-prefix[s-1]))



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
    