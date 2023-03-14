'''

3
1
2

1
8

'''
dy = [1,1,1]
dx = [1,0,-1]
def check(cy,cx,mode):
    if mode:
        board[cy][cx]=cy+1
    else:
        board[cy][cx]=0
    for m in range(1,n+1):
        for d in range(3):
            ny = cy+dy[d]*m
            nx = cx+dx[d]*m
            if 0<=ny<n and 0<=nx<n:
                if mode==1 and board[ny][nx]==0:
                    board[ny][nx]=cy+1
                elif mode==0 and board[ny][nx]==cy+1:
                    board[ny][nx]=0

def dfs(y):
    global cnt
    if y==n:
        cnt+=1
        return

    for x in range(n):
        if board[y][x]==0:
            check(y,x,1)
            dfs(y+1)
            check(y,x,0)

from pprint import pprint
for tc in range(1,int(input())+1):
    n = int(input())
    cnt = 0
    board = [[0]*n for _ in range(n)]
    lst= []
    dfs(0)
    print(f"#{tc} {cnt}")
    


# def n_queen(s):
#     global ans
#     if s == n+1:
#         ans += 1
#         return
#     for i in range(1,n+1):
#         lst[s] = i
#         # print(lst)
#         for j in range(1,s):
#             # 같은 숫자가 하나라도 있는 경우=> 행에서 걸리는 경우
#             if lst[s] == lst[j]:
#                 print("same : ", lst)
#                 break
#             # 대각선 => 
#             if abs(lst[s]-lst[j]) == s-j:
#                 print("s-j  : ", lst)
#                 break
#         else:
#             n_queen(s+1)
 
# T = int(input())
# for tc in range(T):
#     n = int(input())
#     ans = 0
#     lst = [0] * (n+1)
#     n_queen(1)
#     print(f'#{tc+1} {ans}')