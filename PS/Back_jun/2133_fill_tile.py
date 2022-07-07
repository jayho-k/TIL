'''
sum(dp[:i-2])*2
이 부분 다시 체크해보기

'''


n = int(input())

dp = [0]*31
dp[2] = 3
for i in range(4,31,2):
    dp[i] = dp[i-2]*3+sum(dp[:i-2])*2+2

print(dp)
