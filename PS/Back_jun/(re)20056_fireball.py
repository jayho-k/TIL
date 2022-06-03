'''

4 2 1
1 1 5 2 2
1 4 7 1 6
'''
def se_di(lst):
    cnt = 0
    for i in lst:
        if i%2 == 0:
            cnt += 1
        else:
            cnt -= 1
    # 즉 다 홀수면 0, 다 짝수면 len(lst) == cnt
    if len(lst) == abs(cnt):
        return 1
    else:
        return 0

def move1(magic):

    for y,x,m,s,d in magic:
        ny = y + dy[d]*s
        nx = x + dx[d]*s
        fire.append([ny,nx,m,s,[d]])

def move2(fire):

    for y,x,m,s,dd in fire:
        for d in dd:
            ny = y + dy[d]*s
            nx = x + dx[d]*s
            fire.append([ny,nx,m,s,[d]])

def after1(fire):
    
    fire.sort()

    t = 0
    # [1] 모두 하나로 합치기 (뒤에서 합칠것임)
    for i in range(len(fire)-1,0,-1):
        # y,x,m,s,d
        # 같은 위치 => 합치기
        if fire[i][0] == fire[i-1][0] and fire[i][1] == fire[i-1][1]:
            fire[i-1][2] += fire[i][2] #질량합
            fire[i-1][3] += fire[i][3] #속력합
            fire[i-1][4] += fire[i][4]
            fire.pop()

def after2(fire):

    # [2] 나누기(2개이상 합쳐진것만)
    # y,x,m,s,d
    for fire_lst in fire:
        if len(fire_lst[4]) >= 2:
            y,x,m,s,d = fire_lst
            dis_m = int(m/5)
            dis_s = int(s/len(fire_lst[4]))
            dicision = se_di(fire_lst[4])

            if dis_m == 0:
                continue

            # 모두짝 or 홀
            if dicision:
                fire.pop(0)
                for dic in [0,2,4,6]:
                    fire.append([y,x,dis_m,dis_s,[dic]])
            # x
            else:
                fire.pop(0)
                for dic in [1,3,5,7]:
                    fire.append([y,x,dis_m,dis_s,[dic]])


n,m,k = map(int, input().split())
dy = [-1,-1,0,1,1,1,0,-1]
dx = [0,1,1,1,0,-1,-1,-1]

# y,x,m,s,d
magic = [list(map(int,input().split())) for _ in range(m)]

fire = []
#cast
for i in range(k):
    if i == 0:
        move1(magic)
        after1(fire)
        after2(fire)
    else:
        move2(fire)
        after1(fire)
        after2(fire)

print(fire)








# n,m,k = map(int, input().split())
# grid = [[0]*n for _ in range(n)]

# dy = [-1,-1,0,1,1,1,0,-1]
# dx = [0,1,1,1,0,-1,-1,-1]

# # y,x,m,s,d
# magic = [list(map(int,input().split())) for _ in range(m)]

# chck = []

# for _ in range(k):
#     for y,x,m,s,d in magic:

#         ny = y + dy[d]*s
#         nx = x + dx[d]*s

#         if 0<=ny<n and 0<=nx<n:
#             chck.append([ny,nx,m,s,d])

#     chck.sort()
#     # 같은지 안같은지 확인

#     i = 1
#     while i <len(chck):
#         jy,jx,jm,js,jd = chck[i]
#         py,px,pm,ps,pd = chck[i-1]

#         if py == jy and px == jx:
#             chck[i][2] += chck[i-1][2]
#             chck[i][3] += chck[i-1][3]
            
#             chck[i].append(pd)
#             chck.pop(i-1)
#         else:
#             i += 1

#     chch = []
#     for c in chck:
#         yc,xc = c[0], c[1]
#         mc = c[2]
#         sc = c[3]
#         dc = c[4:]
#         if len(dc) >= 2:
#             chm = int(mc/5)
#             chs = int(sc/len(dc))
            
#             cnt = 0
#             for i in dc:
#                 t = i%2
#                 if t == 0:
#                     cnt += 1

#             # 모두 홀수이거나 짝수
#             if cnt == len(dc) or cnt == 0:
#                 for d in (0,2,4,6):
#                     nyc = yc + dy[d]*chs
#                     nxc = xc + dx[d]*chs

#                     chck.append([nyc,nxc,chm,chs,d])
                    
#             else:
#                 for d in (1,3,5,7):
#                     nyc = yc + dy[d]*chs
#                     nxc = xc + dx[d]*chs

#                     chck.append([nyc,nxc,chm,chs,d])


# print(chck)


