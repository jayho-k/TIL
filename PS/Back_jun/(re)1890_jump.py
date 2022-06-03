'''

4
2 3 3 1
1 2 1 3
1 2 3 1
3 1 1 0
'''

n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
table = [[0]*n for _ in range(n)]


table[0][0] = 1
for y in range(n):
    for x in range(n):
        if y == n-1 and x == n-1:
            print(table[y][x])
            break
        
        if y + grid[y][x] < n:
            table[y+grid[y][x]][x] += table[y][x]

        if x + grid[y][x] < n:
            table[y][x+grid[y][x]] += table[y][x]