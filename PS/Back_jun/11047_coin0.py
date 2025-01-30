"""
이 동전을 포함 했을 때와 포함하지 않았을때를 나눠서 풀면 됨

10 4200
1
5
10
50
100
500
1000
5000
10000
50000

"""

# n,k = map(int,input().split())
# coins = [int(input()) for _ in range(n)]
# coins.sort(reverse=True)
# print(coins)

# val = 0
# for i in range(len(coins)):
#     if val





def dfs(d,n,val,cnt):
    global ans
    if d == n:
        if val == 0:
            ans = min(ans,cnt)
        return

    if val//coins[d] > 0:
        dfs(d+1,n,val%coins[d],cnt+(val//coins[d])) # 코인을 포함할 경우

    dfs(d+1,n,val,cnt) # 코인을 포함하지 않을 경우    


n,k = map(int,input().split())
coins = [int(input()) for _ in range(n)]
ans = 1e9

coins.sort(reverse=True)

dfs(0,n,k,0)

print(ans)