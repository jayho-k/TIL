'''

사이 값이 있으면 나의 색으로 바꿈
각각을 확인

8방향확인
+1값이 상대의 돌이고,
+2값이 자신의 돌

1
4 12
1 2 1
1 1 2
4 3 1
4 4 2
2 1 1
4 2 2
3 4 1
1 3 2
2 4 1
1 4 2
4 1 2
3 1 2
'''
from pprint import pprint
def find_enemy(color):
    if color==1:
        return 2
    else:
        return 1

def count_color(board,n):
    f = 0
    s = 0
    for y in range(1,n+1):
        for x in range(1,n+1):
            if board[y][x]==1:
                f+=1
            elif board[y][x]==2:
                s+=1
    return f,s

def setting(board,n):
    board[n//2][n//2]=2
    board[n//2][n//2+1]=1
    board[n//2+1][n//2]=2
    board[n//2+1][n//2+1]=2
    return board

for tc in range(1,int(input())+1):
    n,m = map(int,input().split())
    board = [[0]*(n+1) for _ in range(n+1)]
    board = setting(board,n)
    dy = [-1,0,1,1,1,0,-1,-1]
    dx = [1,1,1,0,-1,-1,-1,0]
    for _ in range(m):
        y,x,color = map(int,input().split())
        e_color = find_enemy(color)
        board[y][x]=color

        for d in range(8):
            
            # 사이라는 것이 전체를 의미
            i = 1
            tmp_lst = []
            while 1:
                ny = y+dy[d]*i
                nx = x+dx[d]*i
                if 1<=ny<n+1 and 1<=nx<n+1:
                    
                    # 같은 색
                    if board[ny][nx]==color:
                        break
                    
                    # 다른 색
                    elif board[ny][nx]==e_color:
                        i+=1
                        tmp_lst.append((ny,nx))

                    # 없을 경우
                    elif board[ny][nx]==0:
                        tmp_lst=[]
                        break
                
                else:
                    tmp_lst=[]
                    break
            if tmp_lst:
                for ty,tx in tmp_lst:
                    board[ty][tx]=color
        pprint(board)
    s,f = count_color(board,n)
    print(f"#{tc}",s,f)
    








