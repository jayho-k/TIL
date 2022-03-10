'''
- 문제 이해 완료
- 어떻게 구현
뭘해야해?? 
1. 각각의 원소의 이웃한 값들을 다 찾아줘야해
    ==> 이중 for문으로 구현해야함
    => 

2. 그것을 찾고 절대값을 씌워주면 됨

다시 풀어보기
'''
T = int(input())
for tc in range(1,T+1):

    lst = []
    n = int(input())
    for _ in range(n):
        s = list(map(int,input().split()))
        lst.append(s)

    dx = [0,0,1,-1]
    dy = [-1,1,0,0]

    total = 0
    for y in range(len(lst)):
        for x in range(len(lst)):
            for d in range(4):
                nx = x + dx[d]
                ny = y + dy[d]
                # 상하좌우를 봐주는 그런거구나
                if 0 <= nx < len(lst) and 0 <= ny < len(lst):

                    m = abs(lst[y][x] - lst[ny][nx])
                    total += m

    print(f'#{tc} {total}')

                





# for :
#     for:
#         for d in range(4):
#             x == dx[d]
#             nx = x + dx[d]
#             ny = y + dy[d]

#             lst[x][y] - lst[nx][ny]

#             (s,y) (nx,ny)

    
'''
비트연산자 부분집합

프린트만 바꿔주면 된다

'''