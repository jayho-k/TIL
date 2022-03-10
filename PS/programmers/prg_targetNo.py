

def dfs(d, numbers, target, value):
    global cnt
    n = len(numbers)
    if d == n and target == value:
        cnt += 1
        return

    if d == n:
        return

    dfs(d+1, numbers, target, value+numbers[d])
    dfs(d+1, numbers, target, value-numbers[d])

numbers = [1,1,1,1,1]
target = 3
cnt = 0

dfs(0, numbers, target, 0)
print(cnt)


# def solution(numbers, target):
#     lsts = []
#     def f(i,n):
#         if i == n:
#             lsts.append(bit[:n])
#             return

#         bit[i] = '+'
#         f(i+1, n)
#         bit[i] = "-"
#         f(i+1, n)
#     n = len(numbers)
#     bit=[0]*n
#     f(0,n)
    
#     cnt = 0
#     for lst in lsts:
#         lst_sum = list(map(list, zip(lst, numbers)))
#         lst_r = []
#         for i in lst_sum:
#             lst_r += i

#         total = 0
#         for j in range(0,len(lst_r),2):
#             if lst_r[j] == '+':
#                 total += lst_r[j+1]
#             else:
#                 total -= lst_r[j+1]
        
#         if total == target:
#             cnt += 1
    
#     answer = cnt
#     return answer