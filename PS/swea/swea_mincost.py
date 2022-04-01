'''
3
73 21 21
11 59 40
24 31 83

'''
# def dfs(d,v):
#     global mn

#     if d == n:
#         mn = min(mn, v)
#         return


#     for i in range(n):
#         if visited[i] == 0:
#             visited[i] = 1
#             dfs(d+1, v+grid[d][i])
#             visited[i] = 0

# n = int(input())
# grid = [list(map(int, input().split())) for _ in range(n)]
# print(grid)
# visited = [0]*n

# mn = 1e9
# dfs(0,0)
# print(mn)

from itertools import permutations

n = int(input())
grid = [list(map(int, input().split())) for _ in range(n)]
tmp = list(range(n))
lst = list(permutations(tmp,n))

mn = 1e9
for l in lst:
    total = 0
    for i in range(n):
        total += grid[i][l[i]]
    mn = min(mn, total)

print(mn)





# y = 0
# while y<n:
#     grid[y]

#     y+=1