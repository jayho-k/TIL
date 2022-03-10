'''
그리드?


7
4 50
2 160
3 30
1 60
3 20
1 100


'''

n = int(input())
lst = []

mx = 0
my = 0
for _ in range(6):
    dirc , m = map(int, input().split())
    lst.append(m)
    if dirc ==1 or dirc == 2:
        if mx < m:
            mx = m
    else:
        if my < m:
            my = m 

big_box = mx * my
mx_i = lst.index(mx)
my_i = lst.index(my)
lst = lst*2

sx1 = lst[mx_i+1]
sx2 = lst[mx_i-1]
sy1 = lst[my_i+1]
sy2 = lst[my_i-1]
# print(sx1)
# print(sx2)
# print(sy1)
# print(sy2)


# print(lst)

sx = max(sx1, sx2) - min(sx1, sx2)
sy = max(sy1, sy2) - min(sy1, sy2)
sm_box = sx * sy

box = big_box - sm_box
# print(box)
print(box*n)



# n = int(input())

# dircs = [0,1,2,3,4]
# dx = [0, 1, -1, 0, 0]
# dy = [0, 0, 0, -1, 1]

# lst = []
# dirc_lst = []

# mx = 0
# my = 0
# for _ in range(6):
#     dirc , m = map(int, input().split())
#     if dirc ==1 or dirc == 2:
#         if mx < m:
#             mx = m
#     else:
#         if my < m:
#             my = m 
#     lst.append(m)
#     dirc_lst.append(dirc)

# jum = [0, 0]
# jum_lst = []
# for i in range(len(lst)):
#     nx = dx[dirc_lst[i]] * lst[i]
#     ny = dy[dirc_lst[i]] * lst[i]
#     jum[0] += nx
#     jum[1] += ny
#     n = [jum[0] + mx, jum[1] + my]
#     jum_lst.append(n)

# print(jum_lst)