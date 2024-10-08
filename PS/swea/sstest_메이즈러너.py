from collections import defaultdict
from pprint import pprint

def move():
    global exit_num
    n_persons_set = set()
    n_persons_grid = [[0]*n for _ in range(n)]

    move_total = 0
    for y,x in persons_set:
        
        cur = abs(y-ey) + abs(x-ex)
        per_cnt = persons_grid[y][x]

        for d in range(4):
            ny = y+dy[d]
            nx = x+dx[d]
            if 0<=ny<n and 0<=nx<n and grid[ny][nx]==0:
                nxt = abs(ny-ey) + abs(nx-ex)

                # 탈출 가능
                if nxt==0:
                    exit_num += per_cnt
                    exit_lst.append((ny,nx))
                    move_total+=(per_cnt)
                    break
                
                # 움직일 수 있음
                elif nxt < cur:
                    n_persons_set.add((ny,nx))
                    n_persons_grid[ny][nx] += per_cnt
                    move_total+=(per_cnt)
                    break
        else:
            n_persons_set.add((y,x))
            n_persons_grid[y][x] += per_cnt

    return n_persons_grid,n_persons_set,move_total

def find_sqaure():
    
    for i in range(2,n+1):
        for y in range(n-i+1):
            for x in range(n-i+1):
                is_exit = False
                is_person = False
                for yy in range(y,y+i):
                    for xx in range(x,x+i):
                        if (yy,xx)==(ey,ex):
                            is_exit = True
                        
                        if (yy,xx) in persons_set:
                            is_person = True

                if is_exit and is_person:
                    # 크기, 좌표
                    return i,y,x
                

def rotate(size,point_y,point_x,ey,ex):

    n_grid = [[0]*n for _ in range(n)]
    n_persons_grid = [[0]*n for _ in range(n)]
    n_persons_set = set()
    rotate_set = set()
    
    flag = True

    for y in range(size):
        for x in range(size):
            n_grid[point_y+y][point_x+x] = grid[point_y+size-x-1][point_x+y]
            n_persons_grid[point_y+y][point_x+x] = persons_grid[point_y+size-x-1][point_x+y]

            if flag and (ey,ex) == (point_y+size-x-1,point_x+y):
                ey = point_y+y
                ex = point_x+x
                flag = False

            rotate_set.add((point_y+y,point_x+x))


    for ry in range(n):
        for rx in range(n):
            if (ry,rx) in rotate_set and n_grid[ry][rx]!=0:
                n_grid[ry][rx]-=1

            elif (ry,rx) not in rotate_set:
                n_grid[ry][rx] = grid[ry][rx]
                n_persons_grid[ry][rx] = persons_grid[ry][rx]

            if n_persons_grid[ry][rx] != 0:
                n_persons_set.add((ry,rx))


    return n_grid,ey,ex,n_persons_grid,n_persons_set


# setting
n,m,k = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
dy = [-1,1,0,0]
dx = [0,0,-1,1]

persons = []
persons_grid = [[0]*n for _ in range(n)]
persons_set = set()
total_per = 0
exit_num = 0
exit_lst = []

for _ in range(m):
    py,px = map(int,input().split())
    persons.append((py-1,px-1))
    persons_grid[py-1][px-1] += 1
    persons_set.add((py-1,px-1))
    total_per+=1

ey,ex = map(int,input().split())
ey-=1
ex-=1
total = 0


for _ in range(k):
    persons_grid,persons_set,move_total = move()
    # print(persons_set, exit_num, total_per)
    # pprint(persons_grid)
    total+=move_total

    if total_per<=exit_num:
        break

    size,point_y,point_x = find_sqaure()

    grid,ey,ex,persons_grid,persons_set = rotate(size,point_y,point_x,ey,ex)


print(total)
print(ey+1,ex+1)


"""
5 3 8
0 0 0 0 1
9 2 2 0 0
0 1 0 1 0
0 0 0 1 0
0 0 0 0 0
1 3
3 1
3 5
3 3
"""



# from collections import defaultdict
# from pprint import pprint

# def move():
#     n_persons = []

#     # exit_per = 0
#     move_total = 0
#     for pi in range(len(persons)):
#         y,x = persons[pi]
#         cur = abs(y-ey) + abs(x-ex)
#         for d in range(4):
#             ny = y+dy[d]
#             nx = x+dx[d]
#             if 0<=ny<n and 0<=nx<n and grid[ny][nx]==0:
#                 nxt = abs(ny-ey) + abs(nx-ex)
#                 # print('y,x,ny,nx,ey,ex,cur,nxt')
#                 # print(y,x,ny,nx,ey,ex,cur,nxt)
#                 # 탈출 가능
#                 if nxt==0:
#                     exit_lst.append((ny,nx))
#                     move_total+=1
#                     # exit_per+=1
#                     break
                
#                 # 움직일 수 있음
#                 elif nxt < cur:
#                     n_persons.append((ny,nx))
#                     move_total+=1
#                     break
#         else:
#             n_persons.append((y,x))

#     return n_persons,move_total

# def find_sqaure():
    
#     for i in range(2,n+1):
#         for y in range(n-i+1):
#             for x in range(n-i+1):
#                 is_exit = False
#                 is_person = False
#                 for yy in range(y,y+i):
#                     for xx in range(x,x+i):
#                         if (yy,xx)==(ey,ex):
#                             is_exit = True
                        
#                         if (yy,xx) in persons:
#                             is_person = True

#                 if is_exit and is_person:
#                     # 크기, 좌표
#                     return i,y,x
                

# def rotate(size,point_y,point_x,ey,ex,persons):
#     n_grid = [[0]*n for _ in range(n)]
#     n_persons = []
#     rotate_set = set()
#     flag = True
#     tmp = set()
#     for y in range(size):
#         for x in range(size):
#             n_grid[point_y+y][point_x+x] = grid[point_y+size-x-1][point_x+y]
#             if flag and (ey,ex) == (point_y+size-x-1,point_x+y):
#                 ey = point_y+y
#                 ex = point_x+x
#                 flag = False

#             for py,px in persons:
#                 if (py,px) == (point_y+size-x-1,point_x+y):
#                     n_persons.append((point_y+y,point_x+x))
#                     tmp.add((py,px))   

#             rotate_set.add((point_y+y,point_x+x))

#     for py,px in persons:
#         if (py,px) not in tmp:
#             n_persons.append((py,px))

#     # pprint(n_grid)
#     # print(rotate_set)
#     for ry in range(n):
#         for rx in range(n):
#             if (ry,rx) in rotate_set and n_grid[ry][rx]!=0:
#                 n_grid[ry][rx]-=1

#             elif (ry,rx) not in rotate_set:
#                 n_grid[ry][rx] = grid[ry][rx]             

#     return n_grid,ey,ex,n_persons


# # setting
# n,m,k = map(int,input().split())
# grid = [list(map(int,input().split())) for _ in range(n)]
# dy = [-1,1,0,0]
# dx = [0,0,-1,1]

# persons = []
# total_per = 0
# exit_num = 0
# exit_lst = []

# for _ in range(m):
#     py,px = map(int,input().split())
#     persons.append((py-1,px-1))
#     total_per+=1

# ey,ex = map(int,input().split())
# ey-=1
# ex-=1
# total = 0
# for _ in range(k):
#     persons,move_total = move()
#     total+=move_total
#     # print(persons,exit_lst)

#     if total_per<=len(exit_lst):
#         break

#     size,point_y,point_x = find_sqaure()
#     grid,ey,ex,persons = rotate(size,point_y,point_x,ey,ex,persons)


# print(total)
# print(ey+1,ex+1)