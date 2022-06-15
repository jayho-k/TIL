'''
3
2 2
1 5
13 29

1
3 7
'''
from pprint import pprint
T = int(input())
for tc in range(1,T+1):
    
    st,fr = map(int,input().split())
    dp = [[0]*31 for _ in range(31)]
    
    for s in range(1,31):
        for f in range(1,31):
            if s == 1:
                dp[s][f] = f
                continue

            if s == f:
                dp[s][f] = 1

            elif s < f:
                dp[s][f] = dp[s-1][f-1] + dp[s][f-1]

            
    print(dp[st][fr])
    
    





















# n = int(input())

# s,f = map(int,input().split())


# def fa(d):

#     total = 1
#     for i in range(1,d+1):
#         total *= i

#     return total

# print(fa(5))

# ans = fa(f) // (fa(s)*fa(f-s))
# print(ans)










