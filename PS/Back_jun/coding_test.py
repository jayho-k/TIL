'''
약효능
3 2
1 10
1 1
2 5
'''
def dinamic(medicine,dp):
    for i in range(n-1,-1,-1):
        d,e = medicine[i]

        if d+i>m:
            dp[i]=dp[i+1]

        else:
            dp[i] = max(dp[i+d]+e, dp[i+1])
    return dp

from itertools import permutations
n,m = map(int,input().split())

medicine = []
for _ in range(n):
    d,e = map(int,input().split())
    medicine.append((d,e))

for p in map(list,permutations(medicine,len(medicine))):
    dp = [0]*(n+1)
    dinamic(p,dp)
    print(dp)

