
tmp = []
def dfs(d,idx):

    if d == m:
        print(*tmp)
        return
        

    for i in range(idx,n):

        tmp.append(lst[i])
        dfs(d+1,i)        
        tmp.pop()

n,m = map(int,input().split())
lst = list(map(int,input().split()))
lst.sort()

dfs(0,0)