'''

3 3
1 1 0
1 1 1
1 0 1
1 1 1

11 10
7 4 0
1 1 1 1 1 1 1 1 1 1
1 0 0 0 0 0 0 0 0 1
1 0 0 0 1 1 1 1 0 1
1 0 0 1 1 0 0 0 0 1
1 0 1 1 0 0 0 0 0 1
1 0 0 0 0 0 0 0 0 1
1 0 0 0 0 0 0 1 0 1
1 0 0 0 0 0 1 1 0 1
1 0 0 0 0 0 1 1 0 1
1 0 0 0 0 0 0 0 0 1
1 1 1 1 1 1 1 1 1 1
'''




def move(y,x,d):
    
    global cnt

    # clean
    grid[y][x] = 2
    left_d = (d+3)%4
    left_y = y+dy[left_d]
    left_x = x+dx[left_d]

    if 0<=left_y<n and 0<=left_x<m and grid[left_y][left_x] == 0:
        cnt = 0
        return left_y,left_x,left_d


    cnt += 1
    return y,x,left_d

    # elif (left_y<0 or left_y>=n or left_x<0 or left_x>=m) or grid[left_y][left_x] != 0:

        

def back(y,x,d):
    global flag
    global cnt 
    back_y = y-dy[d]
    back_x = x-dx[d]
    if (back_y<0 or back_y>=n or back_x<0 or back_x>=m) or grid[back_y][back_x] == 1:
        flag = True
        return back_y,back_x,d
    cnt = 0
    return back_y,back_x,d


from pprint import pprint
n,m = map(int,input().split())
y,x,d = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
flag = False
dy=[-1,0,1,0]
dx=[0,1,0,-1]


cnt = 0
while 1:
    y,x,d = move(y,x,d)
    if cnt == 4:
        y,x,d = back(y,x,d)

    if flag==True:
        break

ans=0
for ay in range(n):
    for ax in range(m):
        if grid[ay][ax] == 2:
            ans += 1

print(ans)