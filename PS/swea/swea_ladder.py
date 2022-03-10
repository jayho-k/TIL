'''
탐색
시작: 첫번째 줄에서 1이면 시작
밑으로 간다

한번 한칸 갈때다
언제 방향을 바꿔? : 방향이 하나 더 생겼을때 방향을 바꿔야함

우선순위
1. 항상 남쪽 방향이 먼저야
2. 하지만 자신이 가던 방향은 제거

탐색 => 이동

'''
# 짧은 버전 ==> 이게 키포인트는 지나온 길을 0으로 만들어 준다
T = 10
for tc in range(1, T+1):
    n = int(input())
    grid = []
    for _ in range(100):
        g = list(map(int, input().split()))
        grid.append(g)
    
    y = 99
    x = grid[99].index(2)

    dx = [-1, 1, 0]
    dy = [0, 0, -1]
    # x값과 y값이 정해짐

    stor = [(y,x)]
    cnt = 0
    while y > 0:

        for dirc in range(3):
            nx = x + dx[dirc]
            ny = y + dy[dirc]

            if 0 <= nx < 100 and 0 <= ny < 100 and grid[ny][nx]==1:
                # 외쪽 보고 오른쪽 봐 ==1 이 있으면 ==> 그쪽으로가/ 조건 하나 추가해주면 된다(저장해놓은 값이 아닐때)
                grid[ny][nx] = 0 # 지나온길은 0으로 만들어준다
                y, x = ny, nx # 업데이트

        cnt += 1
    ans = x
    print(f'#{tc} {ans}')

########### 내가 짠 코드
T = 10

for tc in range(1, T+1):
    n = int(input())
    grid = []
    for _ in range(100):
        g = list(map(int, input().split()))
        grid.append(g)
    2
    
    c = -1
    for strt in grid[99]: # 오른쪽으로 이동
        if strt ==2:
            x = c
            y = 99
            break

    dx = [-1, 1, 0]
    dy = [0, 0, -1]
    # x값과 y값이 정해짐

    stor = [(y,x)]
    cnt = 0
    while y > 0:
        for dirc in range(2):
            nx = x + dx[dirc]
            ny = y + dy[dirc]

            if 0 <= nx < 100 and 0 <= ny < 100 and grid[ny][nx]==1 and (ny,nx) not in stor:
                # 외쪽 보고 오른쪽 봐 ==1 이 있으면 ==> 그쪽으로가/ 조건 하나 추가해주면 된다(저장해놓은 값이 아닐때)

                y, x = ny, nx # 업데이트
                stor.append((y,x))
                break
        else:  # 왼쪽 오른쪽을 봤는데 아무것도 없음 ==> 위로가
            nx = x + dx[2]
            ny = y + dy[2]
            x, y = nx, ny
            stor.append((y,x))

        cnt += 1
    ans = stor[-1][1]
    print(f'#{tc} {ans}')