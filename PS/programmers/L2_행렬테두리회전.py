from pprint import pprint
from collections import deque

def make_grid(r,c):
    num = 1
    grid = [[0]*c for _ in range(r)]
    for y in range(r):
        for x in range(c):
            grid[y][x]=num
            num+=1
    return grid
    
def rotate(y1,x1,y2,x2,grid,r,c):
    y_size, x_size = y2-y1, x2-x1
    tmp = []
    dy,dx=[0,1,0,-1],[1,0,-1,0]
    ny,nx = y1,x1
    mn = 1e9
    for d in range(4):
        if d%2==0:
            for _ in range(x_size):
                mn = min(mn,grid[ny][nx])
                tmp.append((ny,nx))
                nx+=dx[d]
        
        else:
            for _ in range(y_size):
                mn = min(mn,grid[ny][nx])
                tmp.append((ny,nx))
                ny+=dy[d]
    
    dic = {}
    
    for i in range(len(tmp)):
        dic[tmp[i]] = grid[tmp[i-1][0]][tmp[i-1][1]]
    
    for j in dic:
        grid[j[0]][j[1]]=dic[j]
    
    return mn,grid
    
    
    
def solution(rows, columns, queries):
    grid = make_grid(rows,columns)    
    
    ans = []
    for i in range(len(queries)):
        y1,x1,y2,x2 = queries[i]
        y1,x1,y2,x2 = y1-1,x1-1,y2-1,x2-1
        mn,grid = rotate(y1,x1,y2,x2,grid,rows,columns)
        ans.append(mn)
    
    return ans

if __name__ == "main":
    solution(6,6,[[2,2,5,4],[3,3,6,6],[5,1,6,3]])

    