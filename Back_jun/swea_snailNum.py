'''
탐색으로 풀것임
dy
dx
잡아서 움직일것임

1. 일단 [0] n x n 으로 판을 깔아줌
2. 오른쪽으로 움직임

3. 갈 곳이 없음 ==> 밑으로
4. 갈곳없음 => 왼쪽
5. => 위로 가는데 그전에 있던곳 전에까지 가야함
6. 반복
오 -> 아래 -> 왼 -> 위

행 순회

else로 방향을 바꿔

한바퀴 다 돌았으면 또 돌아가야함

5 -> 4 4 3 3 2 2 1 1 

첫 수를 저장하고 꽝 부딧친 다음 수를 저장을 해놓는다

조건1: 넘어가면 안됨
    1) 넘어가려한다
        ==> 방향을 바꿔준다

조건2: 지나간 곳은 넘어가지 않음
    1) 지나간 곳을 가려 한다
        ==> 방향을 바꾼다
    2) x
        ==> 그냥 그방향으로 간다

동쪽이면 dx한테 계속 +1을 해주고 싶어

    # num = list(range(1,n2+1))
    # print(num)
#
'''


T = 1
for tc in range(1, T+1):

    n = int(input())
    grid = [[0]*(n) for _ in range(n)]
    n2 = n**2
    x = 0
    y = 0
    dirc = 0
    
    # 동 남 서 북
    dx = [1,0,-1,0]
    dy = [0,1,0,-1]
    i = 1
    stro = [1]
    while i < n2+1:
                       
        if x < 0 or y < 0 or x >= n or y >= n or grid[y][x] in stro:
            # 방향을 바꿔주어야 한다

            x -= dx[dirc]
            y -= dy[dirc]
            stro.append(i)

            # print('dirc',dirc)
            dirc += 1
            i -= 1
            # print('*'*30)
            if dirc == 4:
                dirc = 0

        # print(y, x)

        grid[y][x] = i

        x += dx[dirc]
        y += dy[dirc]
        i += 1

# print(stro)


    print(f'#{tc}')
    for g in grid:
        print(' '.join(map(str, g)))

            

    
    

                




