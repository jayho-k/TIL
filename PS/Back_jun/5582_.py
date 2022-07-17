'''
ABRACADABRA
ECADADABRBCRDARA
'''
from pprint import pprint
import sys


st1 = list(input())
st2 = list(input())

n1 = len(st1)
n2 = len(st2)

dp = [[0]*(n1+1) for _ in range(n2+1)]

mx = 0
for i in range(1,n1+1):
    for j in range(1,n2+1):
        if st1[i-1] == st2[j-1]:
            dp[j][i] = dp[j-1][i-1] +1
            if mx <= dp[j][i]:
                mx = dp[j][i]
            
# pprint(dp)

print(mx)
