'''
5 3
0 0 1 0 0
0 0 2 0 1
0 1 2 0 0
0 0 1 0 0
0 0 0 0 2

'''

def chciken_check(grid):

    store = []
    home = []
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 2:
                store.append((y,x))

            if grid[y][x] == 1:
                home.append((y,x))

    return store,home

def distance():
    mn = 1e9
    for c in open:
        chicken_dis = 0
        for hy,hx in home:
            tmp = 1e9
            for cy,cx in c:
                dis = abs(cy-hy)+abs(cx-hx)
                tmp = min(tmp,dis)
            chicken_dis += tmp

        mn = min(mn,chicken_dis)
    return mn

def dfs():
    pass

from pprint import pprint
from itertools import combinations
n,m = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]

store, home = chciken_check(grid)
open = list(map(list,combinations(store,m)))

mn = distance()

print(mn)



# dfs
from itertools import combinations
from sys import stdin
from collections import deque
from pprint import pprint


def stp(grid):
    lst = []
    h_lst = []
    for y in range(n):
        for x in range(n):
            if grid[y][x] == 2:
                lst.append((y,x))
            if grid[y][x] == 1:
                h_lst.append((y,x))

    return lst, h_lst

st_p_lst = []
def sel(d,m):
    if d == m:
        st_p= []
        for m_i in range(stn):
            if lst[m_i] ==1:
                st_p.append(stp_lst[m_i])
        st_p_lst.append(st_p)

    for i in range(stn):
        if lst[i] == 0:
            lst[i] = 1
            sel(d+1,m)
            lst[i] = 0


n, m = map(int, stdin.readline().split())
grid = [list(map(int, stdin.readline().split())) for _ in range(n)]


stp_lst,h_lst = stp(grid)
stn = len(stp_lst)
lst = [0]*stn
# mn = 1e9

sel(0,m)
ans = 1e9
for s in st_p_lst:
    a_d_lst = []
    for sy, sx in s:
        d_lst = []
        for hy,hx in h_lst:
            d=abs(sy-hy)+abs(sx-hx)
            d_lst.append(d)
        a_d_lst.append(d_lst)

    ans_lst = list(zip(*a_d_lst))
    total = 0
    for l in ans_lst:
        mn = min(l)
        total += mn
    # print(total)

    if ans > total:
        ans = total
print(ans)