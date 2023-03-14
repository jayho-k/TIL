'''

1
4 2 13
6 1 9 7    
9 8 5 8
3 4 5 3
8 2 6 7

1
3 3 10
7 2 9
6 6 6
5 5 7

'''
from itertools import combinations
def sub_set(lst,c):
    mx_bnft = 0
    for i in range(1,len(lst)):
        for com in combinations(lst,i):
            if sum(com)<=c:
                bnft = 0
                for co in com:
                    bnft += co**2
                mx_bnft = max(mx_bnft,bnft)
    return mx_bnft

def make_table():
    table = [[0]*n for _ in range(n)]
    for y in range(n):
        for x in range(n-m+1):
            tmp_lst = grid[y][x:x+m]
            if sum(tmp_lst)>c:
                bnft = sub_set(tmp_lst,c)
            else:
                bnft = 0
                for t in tmp_lst:
                    bnft += t**2
            for i in range(m):
                table[y][x+i] = max(bnft,table[y][x+i])
    return table

def make_store(table):
    store = []
    for y in range(n):
        for x in range(n-m+1):
            cnt = 0
            com = table[y][x]
            for i in range(m):
                if com == table[y][x+i]:
                    cnt+=1
            
            if cnt==m:
                store.append(table[y][x])
                for j in range(m):
                    table[y][x+j]=0
    return store

for tc in range(1,int(input())+1):
    
    n,m,c = map(int,input().split())
    grid =[list(map(int,input().split())) for _ in range(n)]
    
    table = make_table()
    store = make_store(table)

    store.sort(reverse=True)
    ans = sum(store[:2])
    print(f"#{tc} {ans}")


