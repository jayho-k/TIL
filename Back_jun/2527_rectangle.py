'''




'''
import sys


for _ in range(4):
    x1, y1, x2, y2, x3, y3, x4, y4 = map(int,sys.stdin.readline().split())
    lx = (x2-x1) + (x4-x3)
    ly = (y2-y1) + (y4-y3)
    x_lst = [x1,x2,x3,x4]
    y_lst = [y1,y2,y3,y4]
    mx_y = max(y_lst)
    mn_x = min(x_lst)

# 각케이스를 나눠줘야한다

    # if lx<(x4-x1) or ly < (y2-y3) or ly < (y4-y1):
    #     print('d')

    # elif lx == (x4-x1):
    #     if ly == y2-y3 or ly==y4-y1:
    #         print('c')
    #     elif ly> y2-y3 or ly>y4-y1:
    #         print('b')

    # elif ly == (y2-y3) or ly == (y4-y1):
    #     if lx > x4-x1:
    #         print('b')

    # else:
    #     print('a')



    # if y4 == mx_y:
    #     if lx < (x4-x1) or ly < (y4-y1):
    #         print('d')
    #     elif lx == (x4-x1) or ly == (y4-y1):
    #         if  ly>y4-y1 or lx > x4-x1:
    #             print('b')
    #         else:
    #             print('c')
    #     else:
    #         print('a')

    # elif y2 == mx_y:
    #     if lx < (x4-x1) or ly < (y2-y3):
    #         print('d')
    #     elif lx == (x4-x1) or ly == (y2-y3):
    #         if ly> y2-y3 or lx > x4-x1:
    #             print('b')
    #         else:
    #             print('c')
    #     else:
    #         print('a')
    # else:
    #     print('a')




    # if lx < (x4-x1) or ly < (y2-y3) or ly < (y4-y1):
    #     print('d')

    # elif lx == (x4-x1) or ly == (y2-y3) or ly == (y4-y1):
    #     if ly> y2-y3 or ly>y4-y1 or lx > x4-x1:
    #         print('b')
    #     else:
    #         print('c')
    # else:
    #     print('a')








