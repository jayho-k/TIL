'''
5 1 2 1
0 0 0 0 0
0 30 23 0 0
0 0 -1 0 0
0 0 17 46 77
0 0 0 12 0


11 446 20 3
0 0 0 -1 57 0 -1 0 0 0 0 
0 18 0 -1 -1 0 0 0 0 0 45 
64 0 10 0 0 -1 74 0 0 33 0 
0 61 0 0 -1 0 0 0 0 0 -1 
0 66 0 0 0 0 0 0 16 0 0 
7 0 0 0 6 0 0 -1 27 72 0 
0 0 0 0 0 54 0 42 -1 -1 0 
0 0 -1 0 0 0 0 1 0 0 98 
-1 98 68 0 0 75 1 93 0 0 0 
0 0 0 0 77 0 0 -1 0 0 0 
0 -1 0 -1 0 0 0 0 45 0 0 

문제 풀때
1. 디버깅 하는 방법 다시 리마인드
    디버깅 시 문제 다시 읽을 때 주의할 점
    - 읽고 이상한 부분을 확인 후 바로 코드로 넘어가지 않기
    - 읽으면서 이상한 부분 적어가기
    - 다시 전체 로직 생각하기

2. 손으로 써가면서 계산해야함 


문제 풀이
1. 감염된곳 => timer setting하는 것은 나눠서 따로 생각해주어야함
    => visited와 같은 느낌

2. timer보다 작을 때/ timer보다 클때 등등이 언제 일어나는지 확인하기
    => 1e9 setting, 0으로 setting을 확인해보기

3. time 넣을 때 일반화 시키기


5 2 2 1
0 0 0 0 0
0 30 23 0 0
0 0 -1 0 0
0 0 17 46 77
0 0 0 12 0

'''
from collections import defaultdict, deque
from pprint import pprint

def find_trees():
    trees = []
    for y in range(n):
        for x in range(n):            
            # 여기 감염 check
            if grid[y][x]!=-1 and grid[y][x]!=0 and killer_grid[y][x]==0:
                trees.append((y,x))
    return trees

def develop():
    
    for y,x in trees:
        cnt = 0
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]

            # 나무 존재
            if 0<=ny<n and 0<=nx<n and grid[ny][nx]!=-1 and grid[ny][nx]!=0\
                and killer_grid[ny][nx]==0:
                cnt+=1
        grid[y][x]+=cnt


def breed():
    dic = defaultdict(int)
    for y,x in trees:
        tmp = []
        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n:
                # 제초제
                 
                if grid[ny][nx]==0 and killer_grid[ny][nx]==0:
                    tmp.append((ny,nx))

        for ty,tx in tmp:
            dic[(ty,tx)]+=grid[y][x]//len(tmp)
    
    for di in dic:
        trees.append((di[0],di[1]))
        grid[di[0]][di[1]]=dic[di]
    

def spray():
    # find_big
    lst = []
    for y,x in trees:
        total = grid[y][x]
        for d in range(4):
            for i in range(1,k+1):
                ny = y+cdy[d]*i
                nx = x+cdx[d]*i
                if 0<=ny<n and 0<=nx<n:
                    # 나무가 있으면 => 벽x, 빈공간x
                    if grid[ny][nx]!=-1 and grid[ny][nx]!=0:
                        total+=grid[ny][nx]

                    else:
                        break
        lst.append((total,y,x))
    
    lst.sort(key=lambda x :(-x[0],x[1],x[2]))
    _,my,mx = lst[0]
    kill_lst = [(my,mx)]
    for dd in range(4):
        for j in range(1,k+1):
            mny = my+cdy[dd]*j
            mnx = mx+cdx[dd]*j
            if 0<=mny<n and 0<=mnx<n:
                if grid[mny][mnx]!=-1 and grid[mny][mnx]!=0:
                    kill_lst.append((mny,mnx))

                elif grid[mny][mnx]==0:
                    kill_lst.append((mny,mnx))
                    break

                else:
                    break
    return kill_lst

def remove_killer():
    for y in range(n):
        for x in range(n):
            if killer_grid[y][x]<time:
                killer_grid[y][x]=0

def killer():
    global ans
    for y,x in kill_lst:
        ans+=grid[y][x]
        grid[y][x]=0
        killer_grid[y][x] = time-1+c

n,m,k,c = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [-1,0,1,0]
dx = [0,1,0,-1]
cdy = [-1,1,1,-1]
cdx = [1,1,-1,-1]
ans = 0
killer_grid = [[0]*n for _ in range(n)]

ans = 0
for time in range(1,m+1):
    trees = find_trees()
    if trees:
        develop()
        breed()
        kill_lst = spray()
    
    # 제초재 제거
    remove_killer()
    
    if trees:
        killer()
        
print(ans)



# from pprint import pprint
# from collections import defaultdict,deque

# def find_tree():
#     trees = []
#     for y in range(n):
#         for x in range(n):
#             # 나무가 있는 경우(빈공간 x, 감염 x, 벽 x)
#             if grid[y][x]!=0 and grid[y][x]!=-1 and killer_grid[y][x]==0:
#                 trees.append((y,x))
#     return trees

# def develop():
#     for ty,tx in trees:
#         t_cnt = 0
#         for d in range(4):
#             ny = ty+dy[d]
#             nx = tx+dx[d]

#             # 나무가 있는 경우(빈공간 x, 감염 x, 벽 x)
#             if 0<=ny<n and 0<=nx<n and grid[ny][nx]!=0 and grid[ny][nx]!=-1 and killer_grid[ny][nx]==0:
#                 t_cnt+=1
#         grid[ty][tx]+=t_cnt

# def breed():
#     dic = defaultdict(int)
#     for ty,tx in trees:
#         tmp = []
#         for d in range(4):
#             ny = ty+dy[d]
#             nx = tx+dx[d]

#             # 빈공간이고 감염x => 여기서 막아주기 때문에 밑에서는 딱히 신경 ㄴㄴ
#             if 0<=ny<n and 0<=nx<n and grid[ny][nx]==0 and killer_grid[ny][nx]==0:
#                 tmp.append((ny,nx))

#         # 번식하는 과정
#         if tmp:
#             for tmp_y,tmp_x in tmp:
#                 dic[(tmp_y,tmp_x)] += grid[ty][tx]//len(tmp)

#     # 저장되어 있는 것을 더하기
#     for di in dic:
#         grid[di[0]][di[1]]+=dic[di]
#         trees.append(di)

#     return trees

# def find_kill_lst():

#     # 많이 박멸되는 곳 찾기
#     lifes = []
#     for cy,cx in trees:
#         life = grid[cy][cx]
#         for d in range(4):
#             for i in range(1,k+1):
#                 cny = cy+cdy[d]*i
#                 cnx = cx+cdx[d]*i
#                 if 0<=cny<n and 0<=cnx<n:
#                     # 나무가 있는 곳
#                     if grid[cny][cnx]!=0 and grid[cny][cnx]!=-1:
#                         life += grid[cny][cnx]
#                     else:
#                         break
#         lifes.append((life,cy,cx))

#     # 가장많은 킬을 할 수 있는 나무 찾기
#     lifes.sort(key=lambda x : (-x[0],x[1],x[2]))
    
#     _,my,mx = lifes[0]
#     kill_lst = [(my,mx)]
#     for dd in range(4):
#         for j in range(1,k+1):
#             mny = my+cdy[dd]*j
#             mnx = mx+cdx[dd]*j
#             if 0<=mny<n and 0<=mnx<n:

#                 # 빈공간 x, 벽 x => 나무이면
#                 if grid[mny][mnx]!=0 and grid[mny][mnx]!=-1:
#                     kill_lst.append((mny,mnx))

#                 # 빈공간이면                
#                 elif grid[mny][mnx]==0:
#                     kill_lst.append((mny,mnx))
#                     break

#                 # 벽이면
#                 else:
#                     break

#     return kill_lst

# def remove_killer():
#     for kiy2 in range(n):
#         for kix2 in range(n):
#         # 살충제가 있었는데 time이 지났을 때
#             if 0<killer_grid[kiy2][kix2]<time: 
#                 killer_grid[kiy2][kix2]=0


# n,m,k,c = map(int,input().split())
# grid = [list(map(int,input().split())) for _ in range(n)]
# dy = [-1,0,1,0]
# dx = [0,1,0,-1]
# cdy = [-1,1,1,-1]
# cdx = [1,1,-1,-1]
# ans = 0
# # killed = deque([])
# killer_grid = [[0]*n for _ in range(n)]

# for time in range(1,m+1):
#     trees = find_tree()
#     if trees:
#         develop()
#         breed()
#         kill_lst = find_kill_lst()

#     remove_killer()

#     if trees:

#         for ky,kx in kill_lst:

#             # 먼저 계산해서 ans더하기
#             ans+=grid[ky][kx]
#             grid[ky][kx]=0 #여기서 나무를 죽인다.

#             # 살충재 뿌리기
#             killer_grid[ky][kx] = time-1+c #( 현재시간-1 + 지날 시간)

# print(ans)


