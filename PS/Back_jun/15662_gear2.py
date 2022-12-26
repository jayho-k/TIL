'''

N극 = 0
S극 = 1

1 = 시계 방향
-1= 반시계 방향

맞닿는 부분
2,-2

'''
from collections import deque

def gear_rotate(ro_lst):
    for i in range(1,len(ro_lst)):
        gears[i].rotate(ro_lst[i])

def g_setting(gear,direc,n):

    # 초기화
    ro_lst = [0]*(n+1)
    ro_lst[gear] = direc 

    # gear의 다음부분 부터 for문을 돌려서 진행
    nxt_direc = -direc
    for i in range(gear+1,n+1):
        if gears[i-1][2] != gears[i][-2]:
            ro_lst[i] = nxt_direc
            nxt_direc = -nxt_direc

        # 중간에 0회전이 안하는 부분이 있다면 그 뒤는 모두 회전 하지 않음
        else:
            break

    # gear의 전부분 부터 for문을 돌려서 진행
    nxt_direc = -direc
    for i in range(gear-1,0,-1):
        if gears[i+1][-2]!=gears[i][2]:
            ro_lst[i] = nxt_direc
            nxt_direc = -nxt_direc
        else:
            break

    return ro_lst


n = int(input())

# dictionary를 이용하여 gear1~n만들기
gears = dict()
for i in range(1,n+1):
    gears[i] = deque(map(int,list(input())))


k = int(input())
for _ in range(k):
    g_num, direc = map(int,input().split())
    ro_lst = g_setting(g_num,direc,n)
    gear_rotate(ro_lst)

# 정답 도출하기
total = 0
for g in range(1,n+1):
    if gears[g][0]:
        total+=1

print(total)
