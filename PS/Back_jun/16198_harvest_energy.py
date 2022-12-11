'''



'''

def dfs(st):
    global ans
    if len(weight) == 2:
        ans = max(ans,st)
        return
    
    for i in range(1,len(weight)-1):

        nw = weight[i-1]*weight[i+1]
        w = weight.pop(i)
        dfs(st+nw)
        weight.insert(i,w)

n = int(input())
weight = list(map(int,input().split()))
ans = 0
dfs(0)
print(ans)
