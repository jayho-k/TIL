'''
3
1234 3412
1000 1
1 16

set 함수, list를 비교해보기

시간 초과가 나게 된다.
어떤 이유때문에 시간 초과가 나는지 알아볼 필요가 있음

'''

# 3번째 풀이
def bfs(st,fi,command):

    visited = [0]*10000
    q = deque([(st,command)])
    while q:
        num,co = q.popleft()
        if num == fi:
            return co

        for r in range(4):
            new_num,new_co = calculate(register[r],num,co)
            if not visited[new_num]:
                visited[new_num]=1
                q.append((new_num,new_co))

def calculate(register,num,co):
    
    if register == 'd':
        return (num*2)%10000, co+'D'

    elif register == 's':
        if num == 0: num = 10000
        num -= 1
        return num,co+'S'

    elif register == 'l':
        a = num//1000
        b = num%1000
        return b*10+a, co+'L'

    elif register == 'r':
        a = num%10
        b = num//10
        return (a*1000)+b, co+'R'

import sys
from collections import deque
input = sys.stdin.readline
T = int(input())

register = ['d','s','l','r']
for  _ in range(1,T+1):
    s,f = map(int,input().split())
    print(bfs(s,f,''))



# # 두번째 풀이
# def bfs(st,fi,command):

#     register = ['d','s','l','r']
#     visited = [0]*10000
#     q = deque([(st,command)])
#     while q:
#         num,co = q.popleft()
#         if num == fi:
#             return co

#         for r in range(4):
#             new_num,new_co = calculate(register[r],num,co)
#             if visited[new_num]==0:
#                 visited[new_num]=1
#                 q.append((new_num,new_co))


# def calculate(register,num,co):
    
#     if register == 'd':
#         return (num*2)%10000, co+'D'

#     elif register == 's':
#         if num == 0: num = 10000
#         num -= 1
#         return num,co+'S'

#     elif register == 'l':

#         num_lst = list(str(num))
#         if num <10:
#             num_lst.insert(0,'0')
#         if num <100:
#             num_lst.insert(0,'0')
#         if num <1000:
#             num_lst.insert(0,'0')
#         num = int(num_lst[1]+num_lst[2]+num_lst[3]+num_lst[0])
#         return num,co+'L'

#     elif register == 'r':

#         num_lst = list(str(num))
#         if num <10:
#             num_lst.insert(0,'0')
#         if num <100:
#             num_lst.insert(0,'0')
#         if num <1000:
#             num_lst.insert(0,'0')

#         num = int(num_lst[3]+num_lst[0]+num_lst[1]+num_lst[2])
#         return num, co+'R'

# import sys
# from collections import deque
# input = sys.stdin.readline
# T = int(input())
# for  _ in range(1,T+1):

#     s,f = map(int,input().split())
#     print(bfs(s,f,''))






#  1번쨰 풀이

# def D(num):
#     num = (num*2)
#     return num%10000

# def S(num):
#     if num == 0:
#         num = 9999
#     else:
#         num -= 1
#     return num

# def L(num):

#     num_lst = list(str(num))
#     if num <10:
#         num_lst.insert(0,'0')
#     if num <100:
#         num_lst.insert(0,'0')
#     if num <1000:
#         num_lst.insert(0,'0')
#     num = int(num_lst[1]+num_lst[2]+num_lst[3]+num_lst[0])
#     return num

# def R(num):
#     num_lst = list(str(num))
#     if num <10:
#         num_lst.insert(0,'0')
#     if num <100:
#         num_lst.insert(0,'0')
#     if num <1000:
#         num_lst.insert(0,'0')

#     num = int(num_lst[3]+num_lst[0]+num_lst[1]+num_lst[2])
#     return num

# def bfs(st_num,end_num, visited):

#     q = deque([(st_num,'')])

#     while q:
#         num,alpha = q.popleft()
#         visited[num] = 1
#         if num == end_num:
#             print(alpha)
#             return

#         n_num = D(num)
#         if visited[n_num]==0:
#             alpha1 = alpha + 'D'
#             q.append((n_num,alpha1))
#             visited[n_num] = 1

#         n_num = S(num)
#         if visited[n_num]==0:
#             alpha2 = alpha + 'S'
#             q.append((n_num,alpha2))
#             visited[n_num] = 1

#         n_num = L(num)
#         if visited[n_num]==0:
#             alpha3 = alpha + 'L'
#             q.append((n_num,alpha3))
#             visited[n_num] = 1

#         n_num = R(num)
#         if  visited[n_num]==0:
#             alpha4 = alpha + 'R'
#             q.append((n_num,alpha4))
#             visited[n_num] = 1


# from collections import deque
# T = int(input())

# for tc in range(1,T+1):
#     st_num, end_num = map(int,input().split())
#     visited = [0]* 10000
#     bfs(st_num,end_num,visited)

