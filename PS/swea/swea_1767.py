'''
y = 0 or n-1
x = 0 or n-1


1  
7    
0 0 1 0 0 0 0
0 0 1 0 0 0 0
0 0 0 0 0 1 0
0 0 0 0 0 0 0
1 1 0 1 0 0 0
0 1 0 0 0 0 0
0 0 0 0 0 0 0

1. check를 할때 또한 dfs에다가는 절대 return값으로 넣으면 안된다.
global을 통해서 falg를 따로 만들어서 진행 시켜주어야 한다.

2. 일자 체크 + visited가 저장이 되어야하는 경우에는 while문으로 쓰도록 하자

while문의 조건식을 넣을시 끝까지 돌고 다시 확인한다.

'''
from pprint import pprint
def find_core():
    core = []
    for y in range(n):
        for x in range(n):
            if grid[y][x]:
                core.append((y,x))
    return core,len(core)

def can_connect(y,x):
    length = [0,0,0,0]
    for d in range(4):
        ny,nx = y,x
        cnt=0
        # 이 스킬 확인
        while 1<=ny<n-1 and 1<=nx<n-1:
            cnt+=1
            ny += dy[d]
            nx += dx[d]
            if grid[ny][nx]:
                break
        else:
            # 밖에 벗어나면 +=1 추가돼서 저장 될 것
            length[d]=cnt

    return length

def connect(y,x,d,mode):

    while True:
        ny = y+dy[d]
        nx = x+dx[d]
        if 0<=ny<n and 0<=nx<n and grid[ny][nx]!=mode:
            grid[ny][nx]=mode
            y = ny
            x = nx
        else:
            return

def dfs(depth,core_num,val,cnt):
    global mn, d_cnt

    # 이렇게 해야하는 이유
    # 최대한 많은 Core에 전원을 연결해도, 전원이 연결되지 않는 Core가 존재할 수 있다.

    if d_cnt<cnt:
        mn = val
        d_cnt=cnt

    elif d_cnt==cnt:
        mn = min(mn,val)
    
    if depth==core_num:
        return
    
    y,x = core[depth]
    length = can_connect(y,x)

    for d in range(4):
        if length[d]:
            connect(y,x,d,1)
            dfs(depth+1,core_num,val+length[d],cnt+1)
            connect(y,x,d,0)

    dfs(depth+1,core_num,val,cnt)
    


dy = [-1,0,1,0]
dx = [0,1,0,-1]
for tc in range(1,int(input())+1):
    n = int(input())
    grid = [list(map(int,input().split())) for _ in range(n)]
    mn = 1e9
    d_cnt = 0
    core,core_num = find_core()
    dfs(0,core_num,0,0)
    print(f"#{tc} {mn}")
    





# from pprint import pprint
# def find_processor():
#     processor = []
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x]==1:
#                 processor.append((y,x))

#     return processor,len(processor)


# def check(y,x):
    
#     dirct = [0,0,0,0]
#     for d in range(4):
#         cnt = 0
#         ny,nx = y,x
#         while 0<ny<n-1 and 0<nx<n-1:
#             cnt += 1
#             ny += dy[d]
#             nx += dx[d]
#             if grid[ny][nx]:
#                 break
#         else:
#             dirct[d]=cnt
#     return dirct

# def connect(y,x,d,mode):
#     ny,nx = y,x
#     while 0<ny<n-1 and 0<nx<n-1:
#         ny += dy[d]
#         nx += dx[d]
#         grid[ny][nx]=mode
#         # y = ny
#         # x = nx

# def dfs(dp,total,cnt):

#     # 이거를 한 이유 => 두번쨰 dfs때문에 cnt의 값이 항상 core_num값이
#     # 아님 => 따라서 이렇게 진행을 한 것임
    
#     if cnt > result[0]:
#         result[0]=cnt
#         result[1]=total

#     elif cnt==result[0]:
#         if result[1]>total:
#             result[1]=total

#     if dp==core_num:
#         return
    
#     y,x = cores[dp][0],cores[dp][1]
#     dirct = check(y,x)
#     for d in range(4):
#         if dirct[d] == 0:
#             continue
#         connect(y,x,d,1)
#         dfs(dp+1, total+dirct[d],cnt+1)
#         connect(y,x,d,0)

#     # 이부분이 정말 어려움
#     # [0,0,0,0]이 나왔다는 뜻은
#     # power가 있는 곳이던가 아니면 다 막힌 곳이다.
#     # 따라서 cnt를 유지하고 다음으로 넘어가서
#     # cnt를 끝까지 못가게끔 만드는 방법이다.
#     dfs(dp+1,total,cnt)


# dy = [-1,0,1,0]
# dx = [0,1,0,-1]
# for tc in range(1,int(input())+1):
#     n = int(input())

#     grid = [list(map(int,input().split())) for _ in range(n)]
#     cores, core_num = find_processor()
#     visited = [[0]*n for _ in range(n)]
#     result = [0,0]
#     dfs(0,0,0)
#     print(f"#{tc} {result[1]}")





# from itertools import permutations
# from pprint import pprint
# def find_processor():
#     processor = []
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x]==1:
#                 processor.append((y,x))

#     return processor

# def check(y,x,d,cnt,dp):
#     global flag

#     if y==0 or y==n-1 or x==0 or x==n-1:
#         flag = True
#         mn_lst[dp]=min(cnt,mn_lst[dp])
#         return 
    
#     ny = y+dy[d]
#     nx = x+dx[d]
#     if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and grid[ny][nx]==0:
#         visited[ny][nx]=1
#         check(ny,nx,d,cnt+1,dp)
#         visited[ny][nx]=0



# def dfs(y,x,dp,total):
#     global flag, mn_total

#     if mn_total < total:
#         return

#     if dp==procs_num-1:
#         for d in range(4):
#             visited[y][x]=1
#             check(y,x,d,0,dp)
#             if flag:
#                 flag=False
#                 mn_total = min(mn_total, total+mn_lst[dp])
#             visited[y][x]=0
#         return
    

#     for d in range(4):
#         visited[y][x]=1
#         check(y,x,d,0,dp)
#         if flag:
#             flag=False
#             dfs(pr_per[dp+1][0],pr_per[dp+1][1],dp+1,total+mn_lst[dp])
#         visited[y][x]=0


    

# dy = [-1,0,1,0]
# dx = [0,1,0,-1]
# for tc in range(1,int(input())+1):
#     n = int(input())

#     grid = [list(map(int,input().split())) for _ in range(n)]
#     procs = find_processor()
#     procs_num = len(procs)
#     procs_per = list(map(list,permutations(procs,len(procs))))
#     visited = [[0]*n for _ in range(n)]
#     flag = False
#     mn_total = 1e9


#     pr_per = procs_per[0]
#     mn_lst = [1e9]*(procs_num+1)
#     visited = [[0]*n for _ in range(n)]
#     visited[pr_per[0][0]][pr_per[0][1]]=1
#     dfs(pr_per[0][0],pr_per[0][1],0,0)


#     print(pr_per)
#     print(mn_lst)
#     print(mn_total)




# from itertools import permutations
# from pprint import pprint

# def dfs(y,x,cnt,depth,total):
#     global mn_total

#     if mn_total<total:
#         return

#     if mn_lst[depth] <= cnt:
#         return
    
#     if depth==procs_num-1:
#         mn_lst[depth] = cnt
#         mn_total = total
#         # mn_total.append(total)
#         return

#     if y==0 or y==n-1 or x==0 or x==n-1:
#         mn_lst[depth] = cnt
#         visited[pr_per[depth+1][0]][pr_per[depth+1][1]]=1
#         dfs(pr_per[depth+1][0],pr_per[depth+1][1],0,depth+1,total+cnt)
#         visited[pr_per[depth+1][0]][pr_per[depth+1][1]]=0
#         return
    
#     for d in range(4):
#         ny = y+dy[d]
#         nx = x+dx[d]
#         if 0<=ny<n and 0<=nx<n and visited[ny][nx]==0 and grid[ny][nx]==0:
#             visited[ny][nx]=1
#             dfs(ny,nx,cnt+1,depth,total)
#             visited[ny][nx]=0


# def find_processor():
#     processor = []
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x]==1:
#                 processor.append((y,x))
#     return processor

# dy = [-1,0,1,0]
# dx = [0,1,0,-1]
# for tc in range(1,int(input())+1):
#     n = int(input())

#     grid = [list(map(int,input().split())) for _ in range(n)]
#     procs = find_processor()
#     procs_num = len(procs)
#     procs_per = list(permutations(procs,len(procs)))
#     mn_total  = 1e9

#     mn = 1e9
#     visited = [[0]*n for _ in range(n)]
#     pr_per = procs_per[0]
#     visited[pr_per[0][0]][pr_per[0][1]]=1   
#     mn_lst = [1e9]*(procs_num) 
#     dfs(pr_per[0][0],pr_per[0][1],0,0,0)

#     # for pr_per in procs_per:
#     #     mn = 1e9
#     #     total = 0
#     #     mn_lst = [1e9]*(procs_num)
#     #     visited = [[0]*n for _ in range(n)]
#     #     visited[pr_per[0][0]][pr_per[0][1]]=1
#     #     dfs(pr_per[0][0],pr_per[0][1],1,0,0)
#     print(mn_lst)
#     print(mn_total)

    