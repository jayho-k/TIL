'''
이중for문 쓰면 됨
1. 불려진 수는 0으로 바꿈
2. sum 이 0일때 count를 센다
3. bingo_cnt = 3일 때 빙고
4. 이때 몇번째 때인지 알아야한다 => cnt

-> 이중 리스트를 먼저 만든다 5까지
-> 나머지는 그냥 리스트를 만들고 진행

11 12 2 24 10
16 1 13 3 25
6 20 5 21 17
19 4 8 14 9
22 15 7 23 18
5 10 7 16 2
4 22 8 17 13
3 18 1 6 25
12 19 23 14 21
11 24 9 20 15
'''

def bingo():

    cnt = 0
    for n in num:
        cnt += 1
        for y in range(5):
            for x in range(5):
                if grid[y][x] == n:
                    visited[y][x] = 1

        c1 = garo()
        c2 = sero()
        c3,c4 = diagonal()
        # print(c3,c4)
        # print(c1+c2+c3+c4)
        # pprint(visited)

        if c1+c2+c3+c4 >= 3:
            return cnt

def garo():

    complete = 0
    for vy in visited:
        if sum(vy) == 5:
            complete += 1
        
    return complete

def sero():

    complete = 0 
    for x in range(5):
        tmp = 0
        for y in range(5):
            if visited[y][x] == 1:
                tmp += 1
        if tmp == 5:
            complete += 1

    return complete


def diagonal():
    
    tmp1 = 0
    tmp2 = 0
    complete1 = 0
    complete2 = 0
    for y in range(5):
        if visited[y][y] == 1:
            tmp1 += 1
        
        if visited[y][-y-1] == 1:
            tmp2 += 1
    
    if tmp1 == 5:
        complete1 = 1
    if tmp2 == 5:
        complete2 = 1
    
    return complete1, complete2


from pprint import pprint

grid = [list(map(int,input().split())) for _ in range(5)]
visited = [[0]*5 for _ in range(5)]

num = []
for _ in range(5):
    num += list(map(int,input().split()))


cnt = bingo()
print(cnt)








# from pprint import pprint

# lst = [list(map(int, input().split())) for _ in range(5)]

# num_lst = []
# for _ in range(5):
#     l = list(map(int, input().split()))
#     num_lst = num_lst+ l

# cnt = 0

# for num in num_lst:
#     bingo_cnt = 0
#     for i in range(5):
#         for j in range(5):
#             if lst[i][j] == num:
#                 lst[i][j] = -1
#                 break

#     # 대각선
#     total1 = 0
#     total2 = 0
#     for i in range(5):
#         total1 += lst[i][i]
#         total2 += lst[i][-i-1]
#     if total1 == -5:
#         bingo_cnt += 1

#     if total2 == -5:
#         bingo_cnt += 1

    
#     # 가로세로
#     for i in range(5):
#         total3 = 0
#         total4 = 0
#         for j in range(5):
#             total3 += lst[i][j]
#             total4 += lst[j][i]

#         if total3 == -5:
#             bingo_cnt += 1

#         if total4 == -5:
#             bingo_cnt += 1
#         # total4 = 0
    
#     cnt += 1
#     if bingo_cnt >= 3:

#         # print('bingo')
#         # pprint(lst)
#         print(cnt)
#         break



















# lst = []
# for _ in range(5):
#     s = list(map(int, input().split()))
#     lst.append(s)


# num_lst = []
# for _ in range(5):
#     l = list(map(int, input().split()))
#     num_lst = num_lst+ l

# # pprint(lst)


# cnt = 0

# for num in num_lst:
#     bingo_cnt = 0
#     for i in range(5):
#         for j in range(5):
#             if lst[i][j] == num:
#                 lst[i][j] = -1
#                 break

#     # 대각선
#     total1 = 0
#     for i in range(5):
#         total1 += lst[i][i]
#     if total1 == -5:
#         bingo_cnt += 1

#     total2 = 0
#     for i in range(5):
#         total2 += lst[i][-i-1]
#     if total2 == -5:
#         bingo_cnt += 1

    
#     for i in range(5):
#         total3 = 0
#         for j in range(5):
#             total3 += lst[i][j]

#         if total3 == -5:
#             bingo_cnt += 1

#     for i in range(5):
#         total4 = 0
#         for j in range(5):
#             total4 += lst[j][i]
#         if total4 == -5:
#             bingo_cnt += 1
#         # total4 = 0
    
#     cnt += 1
#     if bingo_cnt >= 3:

#         # print('bingo')
#         # pprint(lst)
#         print(cnt)
#         break






















# for num in num_lst:
#     cross1 = 0
#     cross2 = 0
#     garo = 0
#     sero = 0
       
#     cnt += 1
#     for i in range(5):
#         cross1 += lst[i][i]
#         cross2 += lst[i][-i-1]
           
#         for j in range(5):
#             if num == lst[i][j]:
#                 lst[i][j] = -1

#             # 가로
#             garo += lst[i][j]
#             sero += lst[j][i]

#             # 대각선
            

#         if cross1 == -5 or cross2 == -5 or garo == -5 or sero == -5:
            
#             bingo_cnt += 1

            
#             if bingo_cnt == 3:

#                 # print('cross1',cross1)
#                 # print('cross2', cross2)
#                 # print('garo', garo)
#                 # print('sero', sero)

#                 # print()
#                 print('빙고')
#                 print(cnt)
#                 break
        
