'''


'''
import math

n=int(input())

dp = [0]*(n)

dp[2] = 1
dp[3] = 1

for i in range(4,n):
    twmok = i//2
    twnamu = i%2

    trimok = i//3
    trinamu = i%3

    twmn = 1e9
    trimn = 1e9

    if twnamu == 0:
        twmn = min(twmn,dp[twmok]+1)

    else:
        twmn = min(twmn,dp[twmok*twnamu]+1)

    if trinamu == 0:
        trimn = min(trimn,dp[trimok]+1)

    elif trinamu ==1:
        trimn = min(trimn,dp[trimok*trinamu]+1)

    else:
        trimn = min(trimn,dp[trimok*trinamu]+2)


    dp[i] = min(twmn,trimn)

print(dp)





# for tw in range(1, int(n**0.5)+1):
#     dp[2**tw] = tw

# for tr in range(1,int(n**(1/3))+1):
#     dp[3**tr] = tr

# print(dp)