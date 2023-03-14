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

def house_loc(n):
    houses = []
    for y in range(n):
        for x in range(n):
            if grid[y][x]==1:
                houses.append((y,x))
    return houses

def find_mx(houses):
    mx_cnt = 0
    for y in range(n):
        for x in range(n):

            # 홈 과의 거리를 모두 저장
            k_lst = [0]*(2*n+1)
            for hy,hx in houses:
                dif = abs(hy-y) + abs(hx-x) + 1
                k_lst[dif]+=1

            # 집과의 거리 누적
            for j in range(1,len(k_lst)):
                k_lst[j]+=k_lst[j-1]


            # 손익 계산
            for k in range(1,len(k_lst)):
                oc=(k*k)+((k-1)*(k-1))
                if m*k_lst[k]-oc>=0 and mx_cnt<k_lst[k]:
                    mx_cnt=k_lst[k]
    return mx_cnt

for tc in range(1,int(input())+1):
    n,m = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]
    
    # house location
    houses = house_loc(n)
    mx_cnt = find_mx(houses)

    print(f"#{tc} {mx_cnt}")    














# from collections import deque
# from pprint import pprint

# def check(y,x,k,houses):
#     cnt = 0
#     for hy,hx in houses:
#         dif = abs(hy-y) + abs(hx-x)
#         if k-1>=dif:
#             cnt+=1
#     return cnt


# def house_loc(n):
#     houses = []
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x]==1:
#                 houses.append((y,x))
#     return houses

# for tc in range(1,int(input())+1):
#     n,m = map(int,input().split())
#     grid = [list(map(int,input().split())) for _ in range(n)]
#     houses = house_loc(n)
#     mx_bnft = 0
#     mx_hus = 0

#     for k in range(1,2*n+1):
#         oper_cost = k*k+(k-1)*(k-1)
#         mx_cnt = 0

#         for y in range(n):
#             for x in range(n):
#                 cnt = check(y,x,k,houses)
#                 mx_cnt = max(mx_cnt,cnt)

#         bnft = (m*mx_cnt)-oper_cost
#         if bnft>0 and mx_hus<mx_cnt:
#             mx_hus=mx_cnt

#     print(f"#{tc} {mx_hus}")    

