'''



6
5 2 3 4 1 2
2 2 4
4 1 3 6 5
2 4 2
2 1 3
1 2
1 2

8
17 42 46 81 71 8 37 12
4 2 4 5 7
5 1 3 4 5 8
2 2 4
5 1 2 3 7 8
5 1 2 6 7 8
2 5 8
4 1 4 5 8
5 2 4 5 6 7


6
2 2 2 2 2 2
1 3
1 4
1 1
1 2
1 6
1 5

10
1 2 3 4 5 6 7 8 9 10
2 2 10
2 3 1
2 4 2
2 5 3
2 6 4
2 7 5
2 8 6
2 9 7
2 10 8
2 1 9
'''
import sys
from collections import deque
from itertools import combinations


def bfs(cc, visited,no_vi):

    q = deque([cc[0]])
    visited[cc[0]] = 2

    while q:
        strt = q.popleft()
        for s in graph[strt]:
            if visited[s] == no_vi:
                visited[s] = 2
                q.append(s)


input = sys.stdin.readline

n = int(input())
n_lst = list(range(1,n+1))
ppl = [0]+list(map(int,input().split()))
graph = [[] for _ in range(n+1)]
mn = 1e9

for i in range(1,n+1):
    gn, *lst = map(int,input().split())

    for f in lst:
        graph[i].append(f)


# 시작
for i in range(1,n//2+1):
    c_lst = list(map(list,combinations(n_lst, i)))
    print(c_lst)


    # combination + visited처리
    for cc1 in c_lst:
        visited = [2]+[0]*n
        for c in cc1:
            visited[c] = 1
        
        print(visited)

        a = 0
        b = 0
        cc = []

        # combination 반대 만들기
        for vi in range(len(visited)):
            if visited[vi] == 0:
                cc.append(vi)

        # 1차 연결 확인
        bfs(cc, visited, 0)
        
        if 0 not in visited: # 연결 ok

            #2차 연결확인
            bfs(cc1, visited, 1)
            print(visited)
            print('*'*30)

            if 1 not in visited: # 연결 ok
                for i in cc:
                    a += ppl[i]
                for j in cc1:
                    b += ppl[j]

                mn = min(mn, abs(a-b))
                

if mn == 1e9:
    print(-1)
else:
    print(mn)




# import sys
# from collections import deque
# from itertools import combinations


# def bfs(cc, visited):

#     q = deque([cc[0]])
#     visited[cc[0]] = 1

#     while q:
#         strt = q.popleft()
#         for s in graph[strt]:
#             if visited[s] == 0:
#                 visited[s] = 1
#                 q.append(s)


# input = sys.stdin.readline

# n = int(input())
# n_lst = list(range(1,n+1))
# ppl = [0]+list(map(int,input().split()))
# graph = [[] for _ in range(n+1)]
# mn = 1e9

# for i in range(1,n+1):
#     gn, *lst = map(int,input().split())

#     for f in lst:
#         graph[i].append(f)

# for i in range(1,n//2+1):
#     c_lst = list(map(list,combinations(n_lst, i)))

#     for cc1 in c_lst:

#         v1 = [1]+[0]*n
#         for c in cc1:
#             v1[c] = 1

#         a = 0
#         b = 0
#         cc2 = []
#         v2 = [1]
#         for vi in range(1,len(v1)):
#             if v1[vi] == 0:
#                 cc2.append(vi)

#             # 비트마스킹 => 숫자 뒤집기
#             v2.append(v1[vi]^1)

#         bfs(cc1,v2)
#         bfs(cc2,v1)

#         com = [1]*(n+1)
#         if v1 == com and v2 == com:
#             for i in cc1:
#                 a += ppl[i]
#             for j in cc2:
#                 b += ppl[j]

#             mn = min(mn, abs(a-b))

        
# if mn == 1e9:
#     print(-1)
# else:
#     print(mn)
                




                


# import sys
# from collections import deque
# input = sys.stdin.readline

# def bfs(cc, visited):

#     q = deque([cc[0]])
#     visited[cc[0]] = 1

#     while q:
#         strt = q.popleft()
#         for s in graph[strt]:
#             if visited[s] == 0:
#                 visited[s] = 1
#                 q.append(s)


# def dfs(d,st, fin):
#     global mn

#     # if 0 not in visited[1:]:
#     #     return

#     if d == fin:
#         sma = 0
#         smb = 0
#         cc1 = []
#         cc2 = []
#         for vi in range(1,n+1):
#             if visited[vi]==0:
#                 cc1.append(vi)
#             else:
#                 cc2.append(vi)

#         bfs(cc1, visited)

#         if 0 not in visited:
#             for a in cc1:
#                 sma+=ppl[a]
#             for b in cc2:
#                 smb+=ppl[b]

#             if mn > abs(sma-smb):
#                 mn = abs(sma-smb)
#         return

#     for g in graph[st]:
#         if visited[g] == 0:
#             visited[g] = 1
#             dfs(d+1,g,fin)
#             visited[g] = 0

# n = int(input())
# ppl = [0]+list(map(int,input().split()))
# graph = [[] for _ in range(n+1)]

# for i in range(1,n+1):
#     gn, *lst = map(int,input().split())

#     for f in lst:
#         graph[i].append(f)

# mn = 1e9
# fin = 1

# while fin <= n//2+1:

#     for st in range(1,n+1):
#         visited = [1]+[0]*n
#         visited[st] = 1
#         dfs(1,st, fin)

#     fin += 1

# if mn == 1e9:
#     print(-1)
# else:
#     print(mn)