# 대각선
from pprint import pprint
# lst = [list(range(10)) for _ in range(10)]
# pprint(lst)

# def getInitialList(inputData):
#     initialList = []

#     num = 1
#     for i in range(inputData):
#         initialList.append([])
#         for j in range(inputData):
#             initialList[i].append(num)
#             num += 1
#         if(i%2==1):
#             initialList[i].sort(reverse=True)

#     return initialList

# pprint(getInitialList(10))

# lst = getInitialList(10)

# #대각선 출력
# for i in range(len(lst)):
#     print(lst[i][i])

# # 역 대각선
# for i in range(len(lst)):
#     print(lst[i][-i-1])

# for i in range(4):
#     if i%2 == 0:
#         for j in range(4):
#             print(lst[i][j])

#     else:

#         for j in range(4):
#             print(lst[i][-j-1])


# # 전치 행렬

# 대각선 합은?

# total = 0
# for i in range(len(lst)):
#     total += lst[i][i]
#     print(total)


# # 8방향
# dx = [1, -1, 0, 0, 1 ,1, -1, -1]
# dy = [0, 0, 1, -1, 1, -1, -1, 1]


# def zigzeg(num):

#     mx_num = num* num
#     lst = list(range(mx_num))
#     print(lst)


# pprint(zigzeg(10))


# lst = [[1,2,3] for _ in range(3)]
# # 전치행렬
# for i in range(3):
#     for j in range(3):
#         lst[i][j] # 가로로
#         lst[j][i] # 세로로
#         # 따라서
#         if j < i: # i가 작을때만 바꿀께 이유==> 가운데는 안바꿀 꺼
#             lst[i][j], lst[j][i] = lst[j][i], lst[i][j]

# # 전치행렬
# grid = [[0]*3 for _ in range(3)]
# for i in range(3):
#     for j in range(3):
#         # 따라서
#         if j < i: # i가 작을때만 바꿀께 이유==> 가운데는 안바꿀 꺼
#             grid

# zip과 map으로 전치행렬 만들기
lst = [[1,2,3],
       [4,5,6],
       [7,8,9]]

lst = list(map(list, zip(*lst)))
for i in lst:
    print(i)

print("*"*30)

# lst = list(map(list, zip(*lst)))
# for i in lst:
#     print(i)

# print("*"*30)


# lst = list(map(list, zip(*lst[::-1])))
# for i in lst:
#     print(i)
# print("*"*30)

# lst = list(map(list, zip(*lst[::-1])))[::-1]
# for i in lst:
#     print(i)

# 부분집합 만들기
# 원소가 적을 때
# a = [1,2,3]
# bit = [0]*3
# for i in range(2):
#     bit[0] = i
#     for j in range(2):
#         bit[1] = j
#         for k in range(2):
#             bit[2] = k
#             print(bit)
# [0, 0, 0]
# [0, 0, 1]
# [0, 1, 0]
# [0, 1, 1]
# [1, 0, 0]
# [1, 0, 1]
# [1, 1, 0]
# [1, 1, 1]        

# 원소가 많을 때
# 비트연산자를 이용해본다
# 6개의 원소 ==> 64개가 나오게 된다. 0 ~ 63까지
# 먼저 만들어 놓고 비트로 읽어보자
# 1. 64개 숫자를 만듬
'''
1. 64개 숫자를 만듬
2. 
3. if ==> 이게 0이 아니면 부분집합에 포함된것이야

'''
# arr = [3,6,7,1,5,4]

# n = len(arr)

# for i in range(1<<n): # 1을 계속 왼쪽으로 이동시킴 그럼
#     for j in range(n): # 
#         if i & (1<<j): # if ==> 이게 0이 아니면 부분집합에 포함된것이야
#             print(arr[j], end= ", ")
#     print()
# print()


# # 이진검색
# def binarySearcg(a, n, key):

#     start = 0
#     end = n-1
#     while start <= end:
#         middle = (start+end)//2
#         if a[middle] == key:
#             return True

#         elif a[middle] > key: 
#             # end는 오른쪽 애들을 버린거는 뜻이다(찍은 값이 더 크다)
#             end = middle - 1
#         else:
#             start = middle + 1 
#             # 앞쪽을 버린다는 뜻
#     return False

# # 선택 정렬
# def selctionsort(lst, n):
#     for i in range(n-1):
#         minIdx = i
#         for j in range(i+1, n):
#             if lst[minIdx] > lst[j]:
#                 minIdx = j

#         lst[i], lst[minIdx] = lst[minIdx], lst[i]

# # 선택 알고리즘
# def select(lst, k):
#     for i in range(k):
#         minIdx = i
#         for j in range(i + 1, len(lst)):
#             if lst[minIdx] > lst[j]:
#                 minIdx = j
#         lst[i], lst[minIdx] = lst[minIdx], lst[i]
#     return lst[k-1]


