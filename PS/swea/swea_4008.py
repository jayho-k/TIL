'''
1
6
1 4 0 0
1 2 3 4 5 6
'''

def dfs(d,p,m,t,div,val):
    global mx,mn
    if d==n:
        # print("val : ", val)
        mx = max(mx,val)
        mn = min(mn,val)
        return

    if p:
        # print(val)
        dfs(d+1,p-1,m,t,div,val+nums[d])

    if m:
        # print(val)
        dfs(d+1,p,m-1,t,div,val-nums[d])

    if t:
        # print(val)
        dfs(d+1,p,m,t-1,div,val*nums[d])

    if div:
        # print(val)
        dfs(d+1,p,m,t,div-1,int(val/nums[d]))



for tc in range(1,int(input())+1):
    n = int(input())    
    mx = -1e9
    mn = 1e9

    # +,-,*,/
    p,m,t,div = map(int,input().split())
    nums = list(map(int,input().split()))
    
    dfs(1,p,m,t,div,nums[0])
    # for i in range(n):
    print(f"#{tc} {mx-mn}")
