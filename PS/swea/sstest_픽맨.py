"""
4 2
3 1
1 3 5
2 2 7
3 4 6
4 2 2


2 4
2 2
2 3 2
4 3 4

2 7
2 4
2 1 4
2 3 4

1 3
4 1
3 4 2

"""

from collections import deque,defaultdict
from itertools import product
from pprint import pprint

def find_monster():
    copy_m = []
    for mo in monster:
        if monster[mo]:
            for i in range(len(monster[mo])):
                d = monster[mo][i]
                copy_m.append((mo[0],mo[1],d))

    return copy_m

def monster_move(py,px):
    tmp = []
    for mo in monster:
        while monster[mo]:
            y,x = mo[0],mo[1]
            d = monster[mo].popleft()
            for _ in range(8):
                ny = y+mdy[d]
                nx = x+mdx[d]
                # 시체x, 격자내, 픽맨x
                if 0<=ny<4 and 0<=nx<4 and not ghost[(ny,nx)] and (ny,nx) != (py,px):
                    tmp.append((ny,nx,d))
                    break

                else:
                    d=(d+1)%8
            else:
                tmp.append((y,x,d))
    # print(tmp)
    for ty,tx,td in tmp:
        monster[(ty,tx)].append(td)
    # pprint(monster)

def picman_move(py,px):

    # 가장 많이 먹을 수 있는 경우
    mx_loc = []
    mx = -1
    for i in range(64):
        visited = set()
        visited.add((py,px))
        tmp = []
        total = 0
        y, x = py, px
        for d in pic_move[i]:
            ny = y+pdy[d]
            nx = x+pdx[d]
            if 0<=ny<4 and 0<=nx<4:
                if (ny,nx) not in visited:
                    total+=len(monster[(ny,nx)])
                    visited.add((ny,nx))
                tmp.append((ny,nx))
                y,x = ny,nx
            else:
                break
        else:
            if mx<total:
                mx = total
                mx_loc = tmp
                # print(mx)
                # print(mx_loc)
    # 먹기
    # print(mx)
    # print(mx_loc)
    # pprint(monster)
    for mx_y,mx_x in mx_loc:
        while monster[(mx_y,mx_x)]:
            monster[(mx_y, mx_x)].popleft()
            ghost[(mx_y, mx_x)].append(time+1)

    # print('pic_loc : ',mx_loc[-1])
    return mx_loc[-1]

def remove_ghost():
    for y in range(4):
        for x in range(4):
            while ghost[(y,x)] and ghost[(y,x)][0]<time:
                ghost[(y, x)].popleft()

def breed_monster(copy_m):
    for y,x,d in copy_m:
        monster[(y,x)].append(d)

def find_ans():
    ans = 0
    for mo in monster:
        if monster[mo]:
            ans+=len(monster[mo])
    return ans


# init setting
m,t = map(int,input().split())
py,px = map(int,input().split())
py,px = py-1,px-1
pic_move = list(product(range(4),repeat=3))
pic_move.sort()
# print(pic_move)

monster = {}
ghost = {}
for iy in range(4):
    for ix in range(4):
        monster[(iy,ix)]= deque()
        ghost[(iy,ix)] = deque()
for _ in range(m):
    my,mx,d = map(int,input().split())
    monster[(my-1,mx-1)].append(d-1)

mdy = [-1,-1,0,1,1,1,0,-1]
mdx = [0,-1,-1,-1,0,1,1,1]
pdy = [-1,0,1,0]
pdx = [0,-1,0,1]
time = 0

# cycle
for _ in range(t):
    time+=1
    copy_m = find_monster()
    # print('copy1', copy_m)

    monster_move(py,px)
    py,px = picman_move(py,px)
    remove_ghost()

    breed_monster(copy_m)
    # pprint(monster)


# print(py,px)
# print('monster')
# pprint(monster)
# print()
# print('ghost')
# pprint(ghost)
# #
ans = find_ans()
print(ans)


