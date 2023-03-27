'''
1
8
0 0 0 3 0 0 0 0 
0 0 2 0 0 5 0 0 
0 0 5 0 3 0 0 0 
0 0 1 1 0 0 0 4 
0 0 0 0 0 0 0 0 
0 0 0 0 0 0 5 0 
0 0 4 0 0 3 1 0 
2 0 0 4 3 4 0 0 

check point
    1. 이렇게 while문을 통해서 dy,dx를 따져야 할 경우
        => 경계부분에서 어떻게 진행될지 생각해야한다.

    2. 범위 밖이고 반대 방향으로 갈 경우
        => 반대 방향으로만 변경후 다음 ny,nx
    
    3. 범위 밖이고 달팽이 같은 경우
        => 범위를 넘어갈 한칸 뒤로 가고 d+1
        
'''
# from collections import defaultdict
# def play(y,x,d,gy,gx):

#     block_cnt = 0
#     cnt = 0
#     while True:
#         ny = y+dy[d]
#         nx = x+dx[d]
#         if 0<=ny<n and 0<=nx<n:
#             num = board[ny][nx]
#             if num==-1 or ((ny,nx)==(gy,gx) and cnt!=0):
#                 break

#             if num in b_set:
#                 d = block[num][d]
#                 block_cnt += 1

#             # 무언가 순간이동을 했을 경우
#             # => 새로운 ny,nx를 바꾼다.
#             elif num in w_set:
#                 w_lst = warmhall[num]
#                 for w in w_lst:
#                     if (ny,nx)!=w:
#                         ny,nx = w[0],w[1]
#                         break
        
#         # 범위 외에 있을 경우
#         # => 방향만 바꾼다. => 다음 차례에서 다시 원래 위치로 바뀌게 된다.
#         else:
#             block_cnt += 1
#             d = block[5][d]

#         # 초기화
#         cnt+=1
#         y = ny
#         x = nx
#     return block_cnt


# def find_warmhall():
#     warmhall = defaultdict(list)
    
#     for y in range(n):
#         for x in range(n):
#             if board[y][x] in w_set:
#                 warmhall[board[y][x]].append((y,x))        
#     return warmhall

# for tc in range(1,int(input())+1):

#     n = int(input())
#     board = [list(map(int,input().split())) for _ in range(n)]
#     dy = [-1,0,1,0]
#     dx = [0,1,0,-1]

#     block={
#         1:[2,3,1,0],
#         2:[1,3,0,2],
#         3:[3,2,0,1],
#         4:[2,0,3,1],
#         5:[2,3,0,1]
#     }

#     b_set = set((1,2,3,4,5))
#     w_set = set((6,7,8,9,10))
#     warmhall=find_warmhall()
#     mx=0
#     for y in range(n):
#         for x in range(n):
#             if board[y][x]==0:
#                 for d in range(4):
#                     cnt = play(y,x,d,y,x)
#                     mx= max(mx,cnt)
#     print(f"#{tc} {mx}")



# # 달팽이
# from pprint import pprint
# grid = [[0]*5 for _ in range(5)]

# y,x,i = 0,-1,0
# dy = [0,1,0,-1]
# dx = [1,0,-1,0]
# d = 0
# while i<25:
#     ny = y+dy[d]
#     nx = x+dx[d]
#     if 0<=ny<5 and 0<=nx<5 and grid[ny][nx]==0:
#         i+=1
#         grid[ny][nx]=i

#     else:
#         ny-=dy[d]
#         nx-=dx[d]
#         d = (d+1)%4

#     y = ny
#     x = nx

# pprint(grid)
    




