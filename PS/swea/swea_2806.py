'''

3
1
2

1
8

'''
from pprint import pprint
def check(y,x,mode):
    if mode:
        board[y][x]=y+1
    else:
        board[y][x]=0
    for i in range(1,n+1):
        for d in range(3):
            ny = y+dy[d]*i
            nx = x+dx[d]*i
            if 0<=ny<n and 0<=nx<n:
                if mode==1 and board[ny][nx]==0:
                    board[ny][nx]=y+1
                elif mode==0 and board[ny][nx]==y+1:
                    board[ny][nx]=0

def dfs(y):
    global cnt
    if y==n:
        # pprint(board)
        cnt+=1
        return
    
    for x in range(n):
        if board[y][x]==0:
            check(y,x,1)            
            dfs(y+1)
            check(y,x,0)

dy = [1,1,1]
dx = [1,0,-1]
for tc in range(1,int(input())+1):
    n = int(input())
    cnt = 0
    board = [[0]*n for _ in range(n)]
    dfs(0)
    print(cnt)



# dy = [1,1,1]
# dx = [1,0,-1]
# def check(cy,cx,mode):
#     if mode:
#         board[cy][cx]=cy+1
#     else:
#         board[cy][cx]=0
#     for m in range(1,n+1):
#         for d in range(3):
#             ny = cy+dy[d]*m
#             nx = cx+dx[d]*m
#             if 0<=ny<n and 0<=nx<n:
#                 if mode==1 and board[ny][nx]==0:
#                     board[ny][nx]=cy+1
#                 elif mode==0 and board[ny][nx]==cy+1:
#                     board[ny][nx]=0

# def dfs(y):
#     global cnt
#     if y==n:
#         cnt+=1
#         return

#     for x in range(n):
#         if board[y][x]==0:
#             check(y,x,1)
#             dfs(y+1)
#             check(y,x,0)

# from pprint import pprint
# for tc in range(1,int(input())+1):
#     n = int(input())
#     cnt = 0
#     board = [[0]*n for _ in range(n)]
#     lst= []
#     dfs(0)
#     print(f"#{tc} {cnt}")