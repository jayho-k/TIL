'''
n = 3
l = 1


lst = list(range(1,65))
l2d  = []

p = 0
for i in range(8):
    l2d.append(lst[p:p+8])
    p +=8



'''
from pprint import pprint


def div(grid,n,l):

    full = 2**n
    part = 2**l
    ca = full//part
    l3d = []
    for i in range(0,full,part):
        k =0
        for x in range(ca):
            tmp = []
            for y in range(2**l):
                tmp.append(grid[y+i][k:k+2**l])

            l3d.append(tmp)
            k += 2**l

    return l3d

def rot(lst):
    return list(map(list,zip(*lst[::-1])))

n,Q = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range((n**2)-1)]
L = list(map(int,input().split()))

dy = [0,0,1,-1]
dx = [1,-1,0,0]

for q in range(Q):
    l = L[q]
    full = 2**n
    part = 2**l
    prt = div(grid, n, l)

    # 부분을 하나씩 뽑아서 rotation
    n_prt = []
    for p in prt:
        nw_p = rot(p)
        n_prt.append(nw_p)
    l_tmp = list(map(list,zip(*n_prt)))


    # 여기부터
    n_ful = []
    for lt in l_tmp:
        k = 0
        for _ in range(full//2):
            tp = []
            for f in range(k,full//2+k):
                tp += lt[f]
            n_ful.append(tp)
        k+=full//2


    for y in range(full):
        for x in range(full):
            cnt = 0
            for d in range(4):
                ny = y + dy[d]
                nx = x + dx[d]
                if 0<=ny<full and 0<nx<full and n_ful[ny][nx] == 0:
                    cnt += 1
            if cnt >=2:
                n_ful[y][x] -= 1


pprint(n_ful)
            

