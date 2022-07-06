'''




'''

from pprint import pprint
n,h = map(int,input().split())

lst = [int(input()) for _ in range(n)]
grid = [[0]*n for _ in range(h)]


for i in range(n):
    if i%2==0:
        for g in range(lst[i]):
            grid[g][i] = 1
            
    else:
        for g in range(n,n-lst[i],-1):
            grid[g][i] = 1


tmp_lst=[]
for k in range(h):
    tmp_lst.append(grid[k].count(1))

mn = min(tmp_lst)
cnt = tmp_lst.count(mn)

pprint(grid)
print(mn, cnt)