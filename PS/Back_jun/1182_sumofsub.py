'''
5 0
-7 -3 -2 5 8
'''
def dfs(d,n,v):
    global ans

    
    if d == n: # 깊이가 n모든 경우를 다 돌아 봤으면
        if v == s: 
            ans += 1
        return

    dfs(d+1,n,v+lst[d]) # lst의 idx값을 더해준다
    dfs(d+1,n,v) # return한 뒤에 나온값은 빠져 있을 것이기 때문에 그대로 들어가준다
    
n,s = map(int,input().split())
lst = list(map(int,input().split()))
ans = 0
dfs(0,n,0)
if s == 0:
    print(ans-1)
else:
    print(ans)
