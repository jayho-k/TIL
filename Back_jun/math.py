# # 손익분기점
# # 이익이 되는 지점을 알아보는 공식
# # 알아야할 점: math함수, 올림: ceil(), 내림: floor()

# import math
# a, b ,c = map(int, input().split())
# bnft = c - b

# if bnft == 0:
#     print(-1)
    
# else:
#     x = a/ bnft
#     pnt = math.floor(x) + 1
#     if pnt > 0:
#         print(pnt)
#     else:
#         print(-1)

# 벌집 더하기
# 1             --> 1
# 2~7    6개    --> 2
# 8~19   12개   --> 3
# 20~37  18개   --> 4


# # 수열은 while로 풀수 있음 // 하지만 for문도 가능

# n =int(input())

# cnt = 1
# cnt6 = 0
# num_end = 1

# # for i in range(n):
# #     cnt += 1
# #     cnt6 += 6
# #     num_end += cnt6
# #     if n <= num_end:
# #         print(cnt)
# #         break

# while 1:
#     if n == 1:
#         print(cnt)
#         break
#     cnt += 1
#     print('cnt',cnt)
#     cnt6 += 6
#     print('6',cnt6)
#     num_end += cnt6
#     print('end',num_end)
#     print('-'*20)
#     if n <= num_end:
#         print('answer', cnt)
#         break

# 지그재그 수열
# n/m
count = int(input())
num = 1
line = 0
lst = []
lst1 = []

while count > num:
    line += 1
    num += line
    n = line
    m = 1
    for i in range(line):
        lst.append('{}/{}'.format(n,m))
        n -= 1
        m += 1

    if line%2 != 0:
        for i in lst:
            lst1.append(i)
        lst = []

    elif line%2 == 0:
        lst.reverse()
        for i in lst:
            lst1.append(i)
        lst = []
    
print(lst1[count-1])
# 시간 초과

# x = int(input())
# num_list = []

# num = 0
# num_count = 0

# while num_count < x:
#     num += 1
#     num_count += num

# num_count -= num

# if num % 2 == 0:
#     i = x - num_count
#     j = num - i + 1
# else:
#     i = num - (x - num_count) + 1
#     j = x - num_count

# print(f"{i}/{j}")