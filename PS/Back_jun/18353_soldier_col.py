'''
lis ==> nlogn

for 1~n:
    for i

7
15 11 4 8 5 2 4
'''

n = int(input())
lst = list(map(int,input().split()))
dp = [1]*n

# print(lst)

for i in range(1,n):
    for j in range(i):
        if lst[i] < lst[j]:
            dp[i] = max(dp[i],dp[j]+1)
            # print(dp)

mx = max(dp)

print(n-mx)