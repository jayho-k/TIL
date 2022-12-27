'''
3 2
1 2 1 2 1 2


0~n-1
2n-1~n

로봇 (이동시 그 칸의 내구도 감소)
1 : 올리는
n : 내리는 

순서
1. 벨트 회전
2. 앞에 있는 로봇 부터 한칸 이동
    if not : 가만히 있음
    내구도 1이상, 앞에 아무도 없음
3. 올리는 위치에 로봇 올림 (내구도 1이상)
4. 내구도 0인칸의개수 k개이상 break

'''

# 2차풀이
from collections import deque

def belt_rotate(robots,belt):
    robots.rotate()
    belt.rotate()
    
    # putoff
    if robots[n-1]==1:
        robots[n-1]=0
    return robots,belt

def move_robots(robots,belt):
    global n
    for i in range(n-2,-1,-1):
        if robots[i]==1:
            # 앞이 비었고, belt의 내구도가 0이 아니라면
            if robots[i+1]==0 and belt[i+1]!=0:
                robots[i+1]=1
                robots[i]=0
                belt[i+1]-=1
            
    # putoff
    if robots[n-1]==1:
        robots[n-1]=0

    return robots,belt

def puton_robot(robots,belt):
    if belt[0]:
        robots[0]=1
        belt[0]-=1
    return robots,belt

def check_du(belt):
    cnt=0
    for i in range(len(belt)):
        if belt[i]==0:
            cnt+=1
    return cnt


n,k = map(int,input().split())
belt = deque(map(int,input().split()))
robots = deque([0]*(len(belt)))
ans = 0

while True:
    ans += 1
    robots,belt = belt_rotate(robots,belt)
    robots,belt = move_robots(robots,belt)
    cnt = check_du(belt)
    # cnt = belt.count(0)
    if cnt >= k: break

    robots,belt = puton_robot(robots,belt)
    cnt = check_du(belt)
    # cnt = belt.count(0)를 사용할때 시간이 2배로 느려진다.
    if cnt >= k: break

print(ans)








# # 1차 풀이
# def belt_rotation(belt,robot_loc):
    
#     belt.rotate()
#     robot_loc.rotate()
#     return belt,robot_loc


# def robot_on(belt, robot_loc):

#     if belt[0] != 0:
#         robot_loc[0] = 1
#         belt[0] -= 1
#         return belt,robot_loc

#     return belt, robot_loc


# def robot_move(belt, robot_loc):

#     for i in range(len(robot_loc)-2,-1,-1):
#         if robot_loc[i]==1 and robot_loc[i+1]==0 and belt[i+1]!=0:
#             robot_loc[i+1] = 1
#             robot_loc[i] = 0
#             belt[i+1] -= 1

#     return belt, robot_loc

# def zero_check(belt):
#     # cnt = belt.count(0)

#     cnt = 0
#     for b in belt:
#         if b==0:
#             cnt += 1

#     return cnt


# def location_check(robot_loc,n):

#     if robot_loc[n-1] == 1:
#         robot_loc[n-1] = 0

#     return robot_loc


# from collections import deque
# n,k = map(int,input().split())
# belt = deque(list(map(int,input().split())))
# robot_loc = deque([0]*(2*n))


# step = 0
# cnt = 0

# while 1:

#     step += 1

#     belt,robot_loc = belt_rotation(belt,robot_loc)
#     robot_loc = location_check(robot_loc,n)

#     belt, robot_loc = robot_move(belt, robot_loc)
#     robot_loc = location_check(robot_loc,n)
#     cnt1 = zero_check(belt)
#     if cnt1 >= k:
#         break

#     belt, robot_loc = robot_on(belt, robot_loc)
#     cnt2 = zero_check(belt)
#     if cnt2 >= k:
#         break


# print(step)






# print(belt, robot_loc)
# for i in range(25):

#     print()
#     print(i+2)

#     belt,robot_loc = belt_rotation(belt,robot_loc)
#     print(belt, robot_loc)

#     robot_loc = location_check(robot_loc,n)
#     print(belt, robot_loc)

#     belt, robot_loc = robot_move(belt, robot_loc)
#     print(belt, robot_loc)

#     robot_loc = location_check(robot_loc,n)
#     print(belt, robot_loc)


#     belt, robot_loc = robot_on(belt,robot_loc)
#     print(belt, robot_loc)

    

