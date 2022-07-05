'''


'''

def belt_rotation(belt,robot_loc):
    
    belt.rotate()
    robot_loc.rotate()
    return belt,robot_loc


def robot_on(belt, robot_loc):

    if belt[0] != 0:
        robot_loc[0] = 1
        belt[0] -= 1
        return belt,robot_loc

    return belt, robot_loc


def robot_move(belt, robot_loc):

    for i in range(len(robot_loc)-2,-1,-1):
        if robot_loc[i]==1 and robot_loc[i+1]==0 and belt[i+1]!=0:
            robot_loc[i+1] = 1
            robot_loc[i] = 0
            belt[i+1] -= 1

    return belt, robot_loc

def zero_check(belt):
    # cnt = belt.count(0)

    cnt = 0
    for b in belt:
        if b==0:
            cnt += 1

    return cnt


def location_check(robot_loc,n):

    if robot_loc[n-1] == 1:
        robot_loc[n-1] = 0

    return robot_loc


from collections import deque
n,k = map(int,input().split())
belt = deque(list(map(int,input().split())))
robot_loc = deque([0]*(2*n))


step = 0
cnt = 0

while 1:

    step += 1

    belt,robot_loc = belt_rotation(belt,robot_loc)
    robot_loc = location_check(robot_loc,n)

    belt, robot_loc = robot_move(belt, robot_loc)
    robot_loc = location_check(robot_loc,n)
    cnt1 = zero_check(belt)
    if cnt1 >= k:
        break

    belt, robot_loc = robot_on(belt, robot_loc)
    cnt2 = zero_check(belt)
    if cnt2 >= k:
        break


print(step)






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

    

