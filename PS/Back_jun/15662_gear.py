'''
첫째 줄에 톱니바퀴의 개수 T (1 ≤ T ≤ 1,000)가 주어진다. 

둘째 줄부터 T개의 줄에 톱니바퀴의 상태가 가장 왼쪽 톱니바퀴부터 순서대로 주어진다. 상태는 8개의 정수로 이루어져 있고, 12시방향부터 시계방향 순서대로 주어진다. N극은 0, S극은 1로 나타나있다.

다음 줄에는 회전 횟수 K(1 ≤ K ≤ 1,000)가 주어진다. 다음 K개 줄에는 회전시킨 방법이 순서대로 주어진다. 각 방법은 두 개의 정수로 이루어져 있고, 첫 번째 정수는 회전시킨 톱니바퀴의 번호, 두 번째 정수는 방향이다. 방향이 1인 경우는 시계 방향이고, -1인 경우는 반시계 방향이다.

3시 : idx 2
9시 : idx 6

 
4
11111111
11111111
11111111
11111111
3
1 1
2 1
3 1

'''

def play(g_num, direction):
    
    # foreward
    for i in range(g_num,9):
        pass

    # backward
    for j in range(g_num-1,-1,-1):
        pass
    


def check(front, back, ward):

    if front[2]!=back[6]:
        if ward == 'foreward':
            r_rotation(back)

        else:
            r_rotation(front)


def rotation(gear):
    return gear.rotate()

def r_rotation(gear):
    return gear.rotate(-1)


from collections import deque

T = int(input())

gear = [deque(list(map(int,list(input())))) for _ in range(T)]
k = int(input())
order = [list(map(int,input().split())) for _ in range(k)]


print(gear)