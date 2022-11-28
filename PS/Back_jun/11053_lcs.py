'''
6
10 20 10 30 20 50
'''

n = int(input())
lst = list(map(int,input().split()))

dp = [1]*(n)


for i in range(1,n):
    cnt = 0
    for j in range(i):
        if lst[i] > lst[j]:
            dp[i] += 1

    print(dp)

print(max(dp))