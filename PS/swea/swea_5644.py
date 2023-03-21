'''

1
20 3
2 2 3 2 2 2 2 3 3 4 4 3 2 2 3 3 3 2 2 3
4 4 1 4 4 1 4 4 1 1 1 4 1 4 3 3 3 3 3 3
4 4 1 100
7 10 3 40
6 3 2 70

1
20 1
2 2 3 2 2 2 2 3 3 4 4 3 2 2 3 3 3 2 2 3
4 4 1 4 4 1 4 4 1 1 1 4 1 4 3 3 3 3 3 3
4 4 1 100


1
80 7
2 2 2 2 2 2 0 2 2 0 4 0 2 3 3 2 3 3 0 3 3 3 4 3 3 2 1 1 1 0 4 4 4 1 0 2 2 2 1 1 4 1 2 3 4 4 3 0 1 1 0 3 4 0 1 2 2 2 1 1 3 4 4 4 4 4 4 3 2 1 4 4 4 4 3 3 3 0 3 3 
4 4 1 1 2 1 2 3 3 3 4 4 4 4 4 1 1 1 1 1 1 1 1 0 3 3 2 0 4 0 1 3 3 3 2 2 1 0 3 2 3 4 1 0 1 2 2 3 2 0 4 0 3 4 1 1 0 0 3 2 0 0 4 3 3 4 0 4 4 4 4 0 3 0 1 1 4 4 3 0 
4 3 1 170
10 1 3 240
10 5 3 360
10 9 3 350
9 6 2 10
5 1 4 350
1 8 2 450
'''
from itertools import product
for tc in range(1,int(input())+1):
    n,m = map(int,input().split())
    a_move = [0]+list(map(int,input().split()))
    b_move = [0]+list(map(int,input().split()))

    bc = [list(map(int,input().split())) for _ in range(m)]
    p_lst = list(product(range(m), range(m)))

    # setting
    dy = [0,-1,0,1,0]
    dx = [0,0,1,0,-1]
    nax,nay,nbx,nby = 1,1,10,10
    total = 0
    
    # move
    for mv in range(n+1):
        nay += dy[a_move[mv]]
        nax += dx[a_move[mv]]
        nby += dy[b_move[mv]]
        nbx += dx[b_move[mv]]

        # 범위 안에 오는지 확인
        a_bc = [0]*m
        b_bc = [0]*m
        for i in range(m):
            bcx,bcy,c,p = bc[i]
            a_dif = abs(nax-bcx) + abs(nay-bcy)
            b_dif = abs(nbx-bcx) + abs(nby-bcy)
            
            if a_dif<=c: a_bc[i]=p
            if b_dif<=c: b_bc[i]=p

        mx = 0
        for pi in range(len(p_lst)):
            a,b = p_lst[pi]
            if len(p_lst)>1:
                if a==b:
                    mx = max(mx, (a_bc[a]+b_bc[b])//2)
                else:
                    mx = max(mx,(a_bc[a]+b_bc[b]))
            else:
                if a_bc[a] and b_bc[b]:
                    mx = max(mx, (a_bc[a]+b_bc[b])//2)
                else:
                    mx = max(mx,(a_bc[a]+b_bc[b]))

        # print(mx)
        total+=mx
    print(f"#{tc} {total}")




# print('cycle',mv)
# # print('a_mx, b_mx', a_mx, b_mx)
# print('mx', mx)
# print("a_bc",a_bc)
# print("b_bc",b_bc)
# print()