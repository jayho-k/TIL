'''
90 180 270도 회전

10
3
1 2 3
4 5 6
7 8 9
6
6 9 4 7 0 5
8 9 9 2 6 5
6 8 5 4 9 8
2 2 7 7 8 4
7 5 1 9 7 9
8 9 3 9 7 6

'''
from pprint import pprint

def rotate(n,board):
    n_board = [[0]*n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            n_board[y][x] = board[n-1-x][y]
    return n_board

for tc  in range(1,int(input())+1):
    n = int(input())
    board = [list(map(int,input().split())) for _ in range(n)]
    ans_baord = [[] for _ in range(3)]
    for i in range(3):
        board = rotate(n,board)
        for y in range(n):
            ans_baord[i].append(''.join(map(str,board[y])))

    # ans
    print(f'#{tc}')
    for a in zip(*ans_baord):
        print(*a)
