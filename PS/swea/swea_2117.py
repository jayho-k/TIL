'''

마름모 => 경계부분의 이동거리가 같음
1.
어떤 도형이 나온다면 그 경계를 생각하자
경계로 부터 중심까지의 거리를 먼저 생각해주자 

2. 위 방법이 안될 시 구현
구현 할때는 y방향을 기준으로 x가 어떻게 바뀌는지 먼저 생각해본다.


k_lst = [0]*(2*n+1) # 이것을 어떻게 떠올릴 수 있을까?
# 무언가 값마다 개수를 생각해야할 경우 dp를 떠올려 보자
# 이 문제 같은 경우에는 거리마다 몇개가 포함되는지에 대한 문제
# 따라서 각각의 개수를 다 세어주고 누적합을 진행함

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
def find_home():
    home = []
    for y in range(n):
        for x in range(n):
            if grid[y][x]==1:
                home.append((y,x))
    return home

def cal_diff(home):
    mx_cnt = 0

    # 기준은 마름모의 위치
    for y in range(n):
        for x in range(n):

            k_lst = [0]*(2*n+1) # 이것을 어떻게 떠올릴 수 있을까?
            # 무언가 값마다 개수를 생각해야할 경우 dp를 떠올려 보자

            for hy,hx in home:
                diff = abs(hy-y) + abs(hx-x)+1 # 차이 => 마름모와의 경계이다
                k_lst[diff]+=1

            # 각각을 다 더해준다.
            # 왜냐하면 범위를 찾아주기 위해서
            for i in range(1,len(k_lst)):
                k_lst[i]+=k_lst[i-1]

            for k in range(1,len(k_lst)):
                cost = k*k + (k-1)*(k-1)
                if m*k_lst[k] - cost>=0:
                    mx_cnt = max(mx_cnt, k_lst[k])

    return mx_cnt



for tc in range(1,int(input())+1):
    n,m = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]
    
    home = find_home()
    mx_cnt = cal_diff(home)


    print(f"#{tc} {mx_cnt}")    



# from collections import deque
# from pprint import pprint

# def house_loc(n):
#     houses = []
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x]==1:
#                 houses.append((y,x))
#     return houses

# def find_mx(houses):
#     mx_cnt = 0
#     for y in range(n):
#         for x in range(n):

#             # 홈 과의 거리를 모두 저장
#             k_lst = [0]*(2*n+1)
#             for hy,hx in houses:
#                 dif = abs(hy-y) + abs(hx-x) + 1
#                 k_lst[dif]+=1

#             # 집과의 거리 누적
#             for j in range(1,len(k_lst)):
#                 k_lst[j]+=k_lst[j-1]


#             # 손익 계산
#             for k in range(1,len(k_lst)):
#                 oc=(k*k)+((k-1)*(k-1))
#                 if m*k_lst[k]-oc>=0 and mx_cnt<k_lst[k]:
#                     mx_cnt=k_lst[k]
#     return mx_cnt

# for tc in range(1,int(input())+1):
#     n,m = map(int,input().split())
#     grid = [list(map(int,input().split())) for _ in range(n)]
    
#     # house location
#     houses = house_loc(n)
#     mx_cnt = find_mx(houses)

#     print(f"#{tc} {mx_cnt}")    














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

