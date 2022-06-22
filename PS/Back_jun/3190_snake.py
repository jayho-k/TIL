'''
6
3
3 4
2 5
5 3
3
3 D
15 L
17 D


1. 몸길이를 늘림 : append
2. 사과 있음 => 꼬리는 움직이지 않음 : x
3. 사과 없음 => 꼬리가 위치한 칸 없어짐 : popleft



'''
from collections import deque

def move(snake,y,x):
    snake.append((y,x))
    if (y,x) not in apple:
        snake.popleft()

    else:
        apple.remove((y,x))

    return snake



def direction(di,d):
    if di == 'D':
        d = (d+1)%4
    else:
        d = (d-1)%4
    return d


# 초기 세팅
n = int(input())
k = int(input())

apple = set()
for _ in range(k):
    ky,kx = map(int,input().split())
    apple.add((ky-1,kx-1))

l = int(input())
di_t = deque([])
for _ in range(l):
    time, dirc = input().split()
    di_t.append([int(time), dirc])

dy = [0,1,0,-1]
dx = [1,0,-1,0]

snake = deque([(0,0)])
y=x=d=t=0
# t = 1


while 1:
    t+=1
    
    ny = y + dy[d]
    nx = x + dx[d]

    if ny<0 or ny>=n or nx<0 or nx>=n or (ny,nx) in snake:
        # print(1)
        break

    else:
        snake = move(snake,ny,nx)
        y,x = ny,nx
    
    if not di_t:
        continue

    if di_t[0][0] == t:
        ti,di = di_t.popleft()
        d = direction(di,d)


print(t)
