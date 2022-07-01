'''
8
...**..*
......*.
....*...
........
........
.....*..
...**.*.
.....*..
xxx.....
xxxx....
xxxx....
xxxxx...
xxxxx...
xxxxx...
xxx.....
xxxxx...



8
...**..*
......*.
....*...
........
........
.....*..
...**.*.
.....*..
xxxx....
xxxx....
xxxx....
xxxxx...
xxxxx...
xxxxx...
xxx.....
xxxxx...
'''
def play():
    dy = [-1,-1,0,1,1,1,0,-1]
    dx = [0,1,1,1,0,-1,-1,-1]
    check_mine = False

    for y in range(n):
        for x in range(n):

            cnt = 0
            if grid[y][x]=='x' and mine[y][x]=='*':
                visited[y][x] = '*'
                check_mine = True

            if grid[y][x] == '.':
                continue

            elif grid[y][x] == 'x':
                for d in range(8):
                    ny = y+dy[d]
                    nx = x+dx[d]
                    
                    if 0<=ny<n and 0<=nx<n and mine[ny][nx]=='*':
                        cnt += 1
                if visited[y][x] !='*':
                    visited[y][x] = str(cnt)

    return check_mine

def final(mine_check):

    if mine_check:
        for y in range(n):
            for x in range(n):
                if visited[y][x]=='.' and mine[y][x]=='*':
                    visited[y][x] = '*'

    return

from pprint import pprint

n = int(input())

mine = [list(input()) for _ in range(n)]
grid = [list(input()) for _ in range(n)]
visited = [['.']*n for _ in range(n)]

mine_check = play()
final(mine_check)

for v in visited:
    print(''.join(v))






