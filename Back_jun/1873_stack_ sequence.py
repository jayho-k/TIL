'''
push() = lst.append(key)
pop() = pop()

'''
from collections import deque

def w():
    while 1:
        Fnum = number.popleft()
        stack.append(Fnum)
        pm.append('+')
        if i == stack[-1]:
            break
    pm.append('-')
    stack.pop()


n = int(input())
lst = [int(input()) for _ in range(n)]


number = deque(list(range(1,n+1)))

stack = []
pm = []
for i in lst:
    if stack == []:
        w()

    else:
        if stack[-1] == i:
            stack.pop()
            pm.append('-')

        elif stack[-1] != i:
            if i > stack[-1]:
                w()

            else:
                pm = []
                break

if pm == []:
    print('NO')

else:
    for p in pm:
        print(p)










# n = int(input())
# lst = []
# for _ in range(n):
#     lst.append(int(input()))

# number = deque(list(range(1,n+1)))
# # number.popleft()

# stack = []
# pm = []
# for i in lst:
#     if stack == []:
#         while 1:
#             Fnum = number.popleft()
#             stack.append(Fnum)
#             pm.append('+')
#             if i == stack[-1]:
#                 break

#         pm.append('-')
#         stack.pop()
#         continue

#     if stack[-1] == i:
#         stack.pop()
#         pm.append('-')

#     elif stack[-1] != i:
#         if i > stack[-1]:
#             while i != stack[-1]:
#                 Fnum = number.popleft()
#                 stack.append(Fnum)
#                 pm.append('+')

#             stack.pop()
#             pm.append('-')

#         else:
#             pm = []
#             break

# if pm == []:
#     print('NO')

# else:
#     for p in pm:
#         print(p)






# n = int(input())
# lst = []
# for _ in range(n):
#     lst.append(int(input()))

# number = list(range(1,n+1))

# stack = []
# pm = []
# for i in lst:
#     if stack == []:
#         while 1:
#             Fnum = number[0]
#             del number[0]
#             stack.append(Fnum)
#             pm.append('+')
#             if i == stack[-1]:
#                 break

#         pm.append('-')
#         stack.pop()
#         continue

#     if stack[-1] == i:
#         stack.pop()
#         pm.append('-')

#     elif stack[-1] != i:
#         if i > stack[-1]:
#             while i != stack[-1]:
#                 Fnum = number[0]
#                 del number[0]
#                 stack.append(Fnum)
#                 pm.append('+')

#             stack.pop()
#             pm.append('-')

#         else:
#             pm = []
#             break

# if pm == []:
#     print('NO')

# else:
#     for p in pm:
#         print(p)


