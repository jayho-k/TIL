'''

1
8 3
0 0 0 0 0 1 0 0
0 1 0 1 0 0 0 1
0 0 0 0 0 0 0 0
0 0 0 1 0 1 0 0
0 0 1 1 0 0 0 0
0 0 0 0 0 0 0 0
0 0 0 0 1 0 1 0
1 0 0 0 0 0 0 0


'''
from collections import deque
from pprint import pprint

def check(y,x,k,houses):
    
    cnt = 0
    for hy,hx in houses:
        dif = abs(hy-y) + abs(hx-x)
        if k-1>=dif:
            cnt+=1
    return cnt


def house_loc(n):
    houses = []
    for y in range(n):
        for x in range(n):
            if grid[y][x]==1:
                houses.append((y,x))
    return houses

for tc in range(1,int(input())+1):
    n,m = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]
    houses = house_loc(n)
    mx_bnft = 0
    mx_hus = 0
    cnt = check(3,3,3,houses)

    for k in range(1,n//2+1):
        oper_cost = k*k+(k-1)*(k-1)
        mx_cnt = 0


        for y in range(n):
            for x in range(n):
                cnt = check(y,x,k,houses)
                mx_cnt = max(mx_cnt,cnt)
        # print("@@@@@@@@@")
        # print(k,mx_cnt,oper_cost)
        bnft = (m*mx_cnt)-oper_cost
        if mx_bnft<=bnft:
            mx_bnft = bnft
            mx_hus = mx_cnt
        # mx_bnft = max(mx_bnft,bnft)

    print(mx_hus)    

