from itertools import permutations,combinations
from collections import deque
'''
1
5
0 1 1 0 0
0 0 1 0 3
0 1 0 1 0
0 0 0 0 0
1 0 5 0 0
'''

def find_ps():
    people = []
    stair = []
    for y in range(n):
        for x in range(n):
            if grid[y][x]==1:
                people.append((y,x))
            elif grid[y][x]:
                stair.append((y,x,grid[y][x]))
    return people, stair

def distinct(ppl,stair):
    reach_lst = []
    sy,sx = stair[0],stair[1]
    for py,px in ppl:
        reach_lst.append(abs(py-sy)+abs(px-sx))        
    return reach_lst


def lunch(ppl,stair):
    '''
    1. 도착시간 setting
    2. exit할수 있는애들 확인
    3. reach_lst중에 reach한 애들 확인
    '''
    timer = 0
    cur = 0
    # sy,sx = stair[0], stair[1]
    reach_lst = deque(sorted(distinct(ppl,stair))) # 전체 시간을 먼저 세팅
    exit_lst = deque()

    while reach_lst:
        
        timer+=1
        
        while exit_lst and exit_lst[0]==timer:
            exit_lst.popleft()
            cur-=1
        
        while reach_lst[0]<timer:
            if cur<3:
                reach_lst.popleft() #도착시간
                if not reach_lst:
                    timer+=grid[stair[0]][stair[1]]
                    break
                exit_lst.append(timer+grid[stair[0]][stair[1]]) # 도착시간 + 계단 + 1분
                cur+=1
            else:
                break

    return timer

T = int(input()) 
for tc in range(1, T+1):
    
    # setting
    n = int(input())
    grid = [list(map(int, input().split())) for _ in range(n)]
    people, stair = find_ps()
    ans = 1e9
    for i in range(n):
        for ppl1 in combinations(people,i):
            ppl2 = list(set(people)-set(ppl1))
            total = max(lunch(ppl1, stair[0]),lunch(ppl2, stair[1]))
            ans = min(ans,total)
    
    print(f"#{tc} {ans}")





# def find_ps():
#     people = []
#     stair = []
#     for y in range(n):
#         for x in range(n):
#             if grid[y][x]==1:
#                 people.append((y,x))
#             elif grid[y][x]:
#                 stair.append((y,x,grid[y][x]))
#     return people, stair

# def reach_stair(people,stair):
#     reach_lst = []
#     for py,px in people:
#         reach_lst.append(abs(py-stair[0])+abs(px-stair[1]))
#     return reach_lst


# def lunch(people,stair):
#     '''
#     - 현재 계단에 몇명
#     setiing
#     1. 계단에 도착시간 파악하기

#     timer
#     1. timer를 맞춰서 while문으로 감싸기
#     2. exit에 나올 얘들 있는지 확인
#     3. exit에 넣을 수 있으면 넣기
#     '''
#     sy,sx = stair[0],stair[1]
#     timer = 0
#     cur = 0 #현재 몇명있는지

#     # 도착순으로 정렬 되어있음
#     reach_lst = deque(sorted(reach_stair(people,stair)))
    
#     exit = deque()
#     while reach_lst:
#         timer+=1
        
#         # exit에 나올수 있는지 확인
#         while exit and exit[0]==timer:
#             exit.popleft()
#             cur-=1
        
#         # timer보다 작다는 뜻은 계단에 도착했다는 뜻
#         while reach_lst[0]<timer:

#             # 계단에 도착하고, 현재 인원이 3보다 작다면
#             # 들어갈 수 있음
#             if cur<3:
#                 reach_lst.popleft()

#                 # 마지막일 경우 timer설정
#                 if not reach_lst:
#                     timer+=grid[sy][sx]
#                     break
                
#                 # 총걸리는 시간 = 현재 시간 + 계단 이동시간
#                 exit.append(timer+grid[sy][sx])
#                 cur+=1

#             # 3보다 크면 못들어감
#             else:
#                 break

#     return timer



# T = int(input()) 
# for tc in range(1, T+1):
    
#     # setting
#     n = int(input())
#     grid = [list(map(int, input().split())) for _ in range(n)]
#     people, stair = find_ps()
#     total = 1e9
#     # set으로 차집합을 만들어서 2가지의 경우를 만드는 경우
#     for i in range(len(people)):
#         for people1 in map(list,combinations(people, i)):
#             people2 = list(set(people) - set(people1))
#             time = max(lunch(people1, stair[0]), lunch(people2, stair[1]))
#             total = min(total,time)

#     print(total)



# T = int(input())
 
# for tc in range(1, T+1):
    
#     # setting
#     N = int(input())
#     room = [list(map(int, input().split())) for n in range(N)]
#     people = []
#     stair = []
#     for i in range(N):
#         for j in range(N):
#             if room[i][j] == 1:
#                 people.append([i, j])
#             elif room[i][j] >= 2:
#                 stair.append([i, j, room[i][j]])

    

#     # 거리+계단 시간 + 1분을 정해서 넣음
#     # [계단1의 총시간, 계단2의 총시간] * ppl
#     dis = []
#     for i in people:
#         pdis = []
#         for j in stair:
#             pdis.append(abs(i[0] - j[0]) + abs(i[1] - j[1]) + j[2] + 1)
#         dis.append(pdis)


#     res = [] # => step1 or step2를 선택하는 과정
#     stair1 = 0
#     stair2 = 0
#     dis_index = 0 
#     for i in dis:

#         # step1로 가는 것이 더 빠를 경우
#         if i[0] < i[1]:
#             stair1 += 1
#             res.append([i[0], dis_index]) #[걸리는 시간, 순서를 정한 것]

#         # step2로 가는 것이 더 빠를 경우
#         else:
#             stair2 += 1
#             res.append([i[1], dis_index])

#         dis_index += 1
    
#     # 시간이 오래 걸리는 순으로 정렬
#     res.sort()
#     print(res)
#     for i in res:
        
#         # stair에 3명이 이상이 들어간 경우
#         # 1. stair를 몇번째에 들어갔는지 저장
#         # 2. 
#         if stair1 > 3:
#             #걸리는 시간 = min(이동시간 + stair1시간, stair2 => 거리+계단 시간+1분)
#             i[0] = min(i[0] + stair[0][2], dis[i[1]][1])
#             stair1 -= 1
#         if stair2 > 3:
#             i[0] = min(i[0] + stair[1][2], dis[i[1]][0])
#             stair2 -= 1
#     print(res)
    
#     time = []
#     for i in res:
#         time.append(i[0])
#     print("#{} {}".format(tc, max(time)))




