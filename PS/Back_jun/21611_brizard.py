'''

1. 마법 파괴
2. 구슬 이동
3. 구슬 폭발 => 빈칸 이동 => 폭발 반복
4. 구슬 변화()

7 1
0 0 0 0 0 0 0
3 2 1 3 2 3 0
2 1 2 1 2 1 0
2 1 1 0 2 1 1
3 3 2 3 2 1 2
3 3 3 1 3 3 2
2 3 2 2 3 2 3
2 2
'''

from pprint import pprint

# while , for 2, for s
#  방향은 s마다, 거리 2마다, 
def snail(n,y,x,mode,grid):
    snail = [[0]*n for _ in range(n)]
    if mode=='make':
        lst = [(y,x,0)]
    elif mode=='check':
        lst = [(0,0)]

    i = 1
    s = 1
    d = 0
    ch_i = 1
    while True:
        for _ in range(2):
            for _ in range(s):
                if i==n**2:
                    return snail,lst
                ny = y+snail_dy[d]
                nx = x+snail_dx[d]
                if mode=='make':
                    snail[ny][nx] = i
                    lst.append((ny,nx,i))

                elif mode=='check':
                    if grid[ny][nx]!=0:
                        lst.append((grid[ny][nx],ch_i))
                        ch_i+=1
                y = ny
                x = nx
                i+=1
            d=(d+1)%4
        s+=1

def blizzard(d,s,y,x):

    for _ in range(s):
        ny=y+dy[d]
        nx=x+dx[d]
        # dic[grid[ny][nx]]+=1
        grid[ny][nx] = 0
        y=ny
        x=nx

def move_marble():
    # 0인부분을 그냥 넘기고 lst에 저장
    # 
    n_grid = [[0]*n for _ in range(n)]
    _,check_lst = snail(n,n//2,n//2,'check',grid)
    # print(check_lst)
    for y in range(n):
        for x in range(n):
            num = snail_grid[y][x]
            if num > len(check_lst)-1:
                continue

            else:
                marble_number,i = check_lst[num]
                marble_y,marble_x,_=snail_lst[i]
                n_grid[marble_y][marble_x]=marble_number
    
    return n_grid,check_lst

def boom(lst):
    location = []
    tmp = []
    cnt = 0
    for i in range(1,len(lst)):
        by,bx,_ = lst[i-1]
        cy,cx,_ = lst[i]
        if grid[by][bx] == grid[cy][cx]:
            tmp.append((by,bx))
            cnt+=1

        else:
            tmp.append((by,bx))
            cnt+=1
            if cnt>=4:
                location+=tmp
            tmp=[]
            cnt=0

    for y,x in location:
        dic[grid[y][x]]+=1
        grid[y][x] = 0

    if location:
        return True
    else:
        return False

def change(lst):
    n_grid = [[0]*n for _ in range(n)]
    locations = [0]
    tmp = []
    for i in range(2,len(lst)):
        by,bx,_ = lst[i-1]
        cy,cx,_ = lst[i]
        if grid[by][bx] == grid[cy][cx]:
            tmp.append((by,bx))
        else:
            tmp.append((by,bx))
            a = len(tmp)
            b = grid[by][bx]
            locations.append(a)
            locations.append(b)
            tmp=[]
    # print(locations)
    for j in range(1,len(locations)):
        if j >= n**2:
            break
        y,x,_ = lst[j]
        n_grid[y][x]=locations[j]

    return n_grid

# 서남동북
snail_dy = [0,1,0,-1]
snail_dx = [-1,0,1,0]
dy = [0,-1,1,0,0]
dx = [0,0,0,-1,1]
n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
snail_grid,snail_lst = snail(n,n//2,n//2,'make',[])
dic = {
    1:0,
    2:0,
    3:0
}


for _ in range(m):
    d,s = map(int,input().split())
    blizzard(d,s,n//2,n//2)
    grid,_ = move_marble()
    while 1:
        flag = boom(snail_lst)
        grid,_ = move_marble()
        if flag==False:
            break
    grid = change(snail_lst)

total = 0
for d in dic:
    total+= dic[d]*d

print(total)
