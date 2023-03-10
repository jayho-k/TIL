'''
1
4
0 5 3 8
4 0 4 1
2 5 0 3
7 2 3 0

'''
def find_mn(foods_lst):
    mn = 1e9

    for foods in foods_lst:

        afood=foods
        bfood=[]
        for f in range(n):
            if f not in afood:
                bfood.append(f)

        atotal = 0
        btotal = 0
        
        for afy,afx in permutations(afood,2):
            atotal+=grid[afy][afx]

        for bfy,bfx in permutations(bfood,2):
            btotal+=grid[bfy][bfx]
        
        mn = min(mn,abs(atotal-btotal))
    return mn

# from itertools import permutations,combinations
# for tc in range(1,int(input())+1):
#     n = int(input())
#     grid = [list(map(int,input().split())) for _ in range(n)]
#     foods_lst = list(map(list,combinations(range(n),n//2)))
#     mn=find_mn(foods_lst)
#     print(f"#{tc}",mn)


from itertools import permutations
def dfs(d,foods,idx):

    if d==n//2:
        foods_lst.append(foods)  
        return
    
    for i in range(idx,n):
        if visited[i]==0:
            visited[i]=1
            dfs(d+1,foods+[i],i)
            visited[i]=0


for tc in range(1,int(input())+1):
    n = int(input())
    grid = [list(map(int,input().split())) for _ in range(n)]
    visited = [0]*n
    foods_lst = []
    dfs(0,[],0)
    mn=find_mn(foods_lst)
    print(f"#{tc}",mn)

