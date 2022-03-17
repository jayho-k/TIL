'''
+,-,*,/

'''

lst = []
def dfs(d,p,m,t,div,v):

    if d == n:
        lst.append(v)
        return

    if p != 0:
        dfs(d+1,p-1,m,t,div,v+n_lst[d])

    if m != 0:
        dfs(d+1,p,m-1,t,div,v-n_lst[d])

    if t != 0:
        dfs(d+1,p,m,t-1,div,v*n_lst[d])

    if div != 0:
        if v < 0:
            dfs(d+1,p,m,t,div-1,-((-v)//n_lst[d]))
        elif v>=0:
            dfs(d+1,p,m,t,div-1,v//n_lst[d])



n = int(input())
n_lst = list(map(int, input().split()))
oper = list(map(int, input().split()))
p,m,t,div = oper
v = n_lst[0]
dfs(1,p,m,t,div,v)
print(max(lst))
print(min(lst))



