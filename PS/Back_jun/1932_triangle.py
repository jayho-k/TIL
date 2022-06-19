'''
5
7
3 8
8 1 0
2 7 4 4
4 5 2 6 5

30
'''



n = int(input())
lsts = []

for _ in range(n):
    t = list(map(int,input().split()))
    lsts.append(t)

total = 0
for i in range(1,n+1):
    total += i

dp =[]
for i in range(1,n+1):
    dp.append([0]*i)

dp[0] = lsts[0]


for i in range(1,len(lsts)):
    lst = lsts[i]

    for j in range(len(lst)):
        if j == 0:
            dp[i][0] = dp[i-1][0] + lst[0]

        elif j == len(lst)-1:
            dp[i][-1] = dp[i-1][-1] + lst[-1]

        else:
            dp[i][j] = max(dp[i-1][j-1]+lst[j] , dp[i-1][j]+lst[j])

print(max(dp[-1]))