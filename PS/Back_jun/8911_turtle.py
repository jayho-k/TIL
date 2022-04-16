'''
3
FFLF
FFRRFF
FFFBBBRFFFBBB

'''
import sys
input = sys.stdin.readline

T = int(input())
for tc in range(1,T+1):

    y2 = x2 = y1 = x1 = 0
    d = 0
    y,x = 0,0
    dy = [-1,0,1,0]
    dx = [0,1,0,-1]

    order_lst = list(input())

    if 'F' in order_lst or 'B' in order_lst:
        for order in order_lst:

            if order == 'L':
                d -= 1
            elif order == 'R':
                d += 1
            else:
                if order == 'F':
                    ny = y + dy[d%4]
                    nx = x + dx[d%4]
                    
                elif order == 'B':
                    ny = y - dy[d%4]
                    nx = x - dx[d%4]

                y2 = max(y2,ny)
                x2 = max(x2,nx)
                y1 = min(y1,ny)
                x1 = min(x1,nx)
                y = ny
                x = nx

        print(abs(y1-y2)*abs(x1-x2))
        
    else:
        print(0)

        
