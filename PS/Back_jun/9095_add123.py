'''
1+1+1+1
1+1+2
1+2+1
2+1+1
2+2
1+3
3+1

3
4
7
10

  0 1 2 3 4 5 6 7 
0                 

'''

# dp

T = int(input())
for tc in range(1,T+1):
    n = int(input())

    dp = [0]*11
    dp[1] = 1
    dp[2] = 2
    dp[3] = 4

    if n > 3:
        for i in range(4,n+1):
            dp[i] = dp[i-1] + dp[i-2] +dp[i-3]
    
    print(dp[n])






# dfs
def dfs(d):
    global cnt

    if d == n:
        cnt += 1
        return

    elif d > n:
        return

    else:
        dfs(d+1)
        dfs(d+2)
        dfs(d+3)

T = int(input())
for tc in range(1,T+1):

    n = int(input())
    cnt = 0
    dfs(0)

    print(cnt)

