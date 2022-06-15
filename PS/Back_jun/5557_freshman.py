'''
11
8 3 2 4 8 7 2 4 0 8 8
중간에 나오는 수 모두 0 이상 20 이하이어야 한다.

일단은 무조건 ==> 0<=x<=20
1. 더했을 떄
    : 

2. 빼기를 했을때



'''
from pprint import pprint
n = int(input())
dp = [[0]*21 for _ in range(n)]
lst = list(map(int,input().split()))

dp[0][lst[0]] = 1

for y in range(1,n):

    for x in range(21):

        if dp[y-1][x] != 0:

            # 인덱스가 궁금 ==> x 
            # x + 지금 수 / x- 지금수

            # 전에꺼 더하기
            if 0<=x+lst[y]<=20:
                # dp[y][x+lst[y]] += dp[y-1][x+lst[y]]+1
                dp[y][x+lst[y]] += dp[y-1][x]

            # 전에꺼 빼기 위치
            if 0<=x-lst[y]<=20:
                # dp[y][x-lst[y]] += dp[y-1][x-lst[y]]+1
                dp[y][x-lst[y]] += dp[y-1][x]

pprint(dp)
print(dp[-2][lst[-1]])



