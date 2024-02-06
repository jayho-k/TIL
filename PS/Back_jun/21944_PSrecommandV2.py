"""
5
1000 1 1
1001 2 1
19998 78 2
2667 37 3
2042 55 3
12
add 1402 59 1
recommend 1 1
recommend2 1
recommend3 1 50
recommend3 -1 50
solved 1000
solved 2667
recommend 2 1
recommend 1 -1
recommend2 -1
solved 1001
recommend 1 -1


3
19998 78 2
2667 37 3
2042 55 3
6
recommend3 -1 50
solved 2667
recommend3 -1 50
recommend3 1 70
solved 19998
recommend3 1 70



5
1000 1 1
1001 2 1
19998 78 2
2667 37 3
2042 55 3
4
add 1402 59 1
recommend 1 1
recommend2 1
recommend3 1 50

"""


import sys
import heapq
from collections import defaultdict

# setting
rec1 = {}
rec2_h = []
rec2_e = []
rec3 = {}
solved_set = set()
p2l = {}

for i in range(1,101):
    rec1[i]=[]
    rec1[-i]=[]
    rec3[i]=[]
    rec3[-i]=[]

# main
input = sys.stdin.readline
n = int(input())

for _ in range(n):
    p,l,g = map(int,input().split())

    # rec1
    heapq.heappush(rec1[g],(-l,-p)) # 어려운, 번호 큼
    heapq.heappush(rec1[-g],(l,p)) # 쉬운, 번호 작음

    # rec2
    heapq.heappush(rec2_h,(-l,-p)) # 어려운, 번호가 큰
    heapq.heappush(rec2_e,(l,p)) # 쉬운, 번호가 작은

    # rec3, 레벨별로 문제가 존재
    heapq.heappush(rec3[l],p) # 번호가 작은 것
    heapq.heappush(rec3[-l],-p) # 번호가 큰것

    p2l[p]=l


# play
m = int(input())
for _ in range(m):
    
    o,*con = input().split()
    
    if o=='recommend':
        g,x = map(int,con)
        if x==1:
            # solve에 있는 것 pop
            # heapq.heappush(rec1[g],(-l,-p))
            # solved[p].add(l)

            while rec1[g] and -rec1[g][0][1] in solved_set:
                heapq.heappop(rec1[g])
                        
            print(-rec1[g][0][1])
            

        elif x==-1:

            while rec1[-g] and rec1[-g][0][1] in solved_set:
                heapq.heappop(rec1[-g])

            print(rec1[-g][0][1])


    elif o=='recommend2':
        x = int(con[0])

        if x==1:

            
            while rec2_h and -rec2_h[0][1] in solved_set:
                heapq.heappop(rec2_h)
            
            print(-rec2_h[0][1])


        elif x==-1:

            while rec2_e and rec2_e[0][1] in solved_set:
                heapq.heappop(rec2_e)
            
            print(rec2_e[0][1])



    elif o=='recommend3':

        x,l = map(int,con)

        # L난이도 보다 크거나 같은 문제 중 가장 쉬운 문제
        if x==1:

            mn_n = 1e9

            for a in range(l,101):
                while rec3[a] and rec3[a][0] in solved_set:
                    heapq.heappop(rec3[a])

                if rec3[a]:
                    mn_n= rec3[a][0]
                    break
    
            if mn_n!=1e9:
                print(mn_n)
            else:
                print(-1)

        elif x==-1:
            
            mx_n = -1

            for a in range(l,0,-1):
                while rec3[-a] and -rec3[-a][0] in solved_set:
                    heapq.heappop(rec3[-a])

                if rec3[-a]:
                    mx_n= -rec3[-a][0]
                    break

            if mx_n!=-1:
                print(mx_n)
            else:
                print(-1)


    elif o=='add':
        p,l,g = map(int,con)

        # rec1
        heapq.heappush(rec1[g],(-l,-p))
        heapq.heappush(rec1[-g],(l,p))

        # rec2
        heapq.heappush(rec2_h,(-l,-p))
        heapq.heappush(rec2_e,(l,p))

        # rec3
        heapq.heappush(rec3[l],p)
        heapq.heappush(rec3[-l],-p)

        # remove
        # 같은 번호 + 같은 난이도가 있다면 remove
        if p in solved_set:
            solved_set.remove(p)


    elif o=='solved':
        p = int(con[0])
        solved_set.add(p)



















# import sys
# import heapq
# from collections import defaultdict

# # setting
# rec1 = {}
# rec2_h = []
# rec2_e = []
# rec3 = {}
# # solved = defaultdict(set)
# solved_set = set()
# p2l = {}

# for i in range(1,101):
#     rec1[i]=[]
#     rec1[-i]=[]
#     rec3[i]=[]
#     rec3[-i]=[]

# # main
# input = sys.stdin.readline
# n = int(input())

# for _ in range(n):
#     p,l,g = map(int,input().split())

#     # rec1
#     heapq.heappush(rec1[g],(-l,-p)) # 어려운, 번호 큼
#     heapq.heappush(rec1[-g],(l,p)) # 쉬운, 번호 작음

#     # rec2
#     heapq.heappush(rec2_h,(-l,-p)) # 어려운, 번호가 큰
#     heapq.heappush(rec2_e,(l,p)) # 쉬운, 번호가 작은

#     # rec3, 레벨별로 문제가 존재
#     heapq.heappush(rec3[l],p) # 번호가 작은 것
#     heapq.heappush(rec3[-l],-p) # 번호가 큰것

#     p2l[p]=l


# # play
# m = int(input())
# for _ in range(m):
    
#     o,*con = input().split()
    
#     if o=='recommend':
#         g,x = map(int,con)
#         if x==1:
#             # solve에 있는 것 pop
#             # heapq.heappush(rec1[g],(-l,-p))
#             # solved[p].add(l)

#             while rec1[g] and -rec1[g][0][1] in solved_set:
#                 heapq.heappop(rec1[g])
                        

#             # while rec1[g] and -rec1[g][0][1] in solved \
#             #     and -rec1[g][0][0] in solved[-rec1[g][0][1]]:
#             #     heapq.heappop(rec1[g])
            
#             # print(rec1)
#             print(-rec1[g][0][1])
            

#         elif x==-1:

#             # print(solved)
#             # print(rec1[-g])

#             while rec1[-g] and rec1[-g][0][1] in solved_set:
#                 heapq.heappop(rec1[-g])


#             # while rec1[-g] and rec1[-g][0][1] in solved \
#             #     and rec1[-g][0][0] in solved[rec1[-g][0][1]]:
#             #     heapq.heappop(rec1[-g])
            
#             print(rec1[-g][0][1])


#     elif o=='recommend2':
#         x = int(con[0])

#         if x==1:

            
#             while rec2_h and -rec2_h[0][1] in solved_set:
#                 heapq.heappop(rec2_h)
            
#             # while rec2_h and -rec2_h[0][1] in solved \
#             #     and -rec2_h[0][0] in solved[-rec2_h[0][1]]:
#             #     heapq.heappop(rec2_h)
            
#             # print(rec2_h)
#             print(-rec2_h[0][1])


#         elif x==-1:

#             while rec2_e and rec2_e[0][1] in solved_set:
#                 heapq.heappop(rec2_e)

#             # while rec2_e and rec2_e[0][1] in solved \
#             #     and rec2_e[0][0] in solved[rec2_e[0][1]]:
#             #     heapq.heappop(rec2_e)
            
#             print(rec2_e[0][1])



#     elif o=='recommend3':

#         x,l = map(int,con)

#         # L난이도 보다 크거나 같은 문제 중 가장 쉬운 문제
#         if x==1:

#             mn_n = 1e9

#             for a in range(l,101):
                
#                 while rec3[a] and rec3[a][0] in solved_set:
#                     heapq.heappop(rec3[a])

#                 # while rec3[a] and rec3[a][0] in solved\
#                 #     and a in solved[rec3[a][0]]:
#                 #     heapq.heappop(rec3[a])

#                 if rec3[a]:
#                     mn_n= rec3[a][0]
#                     break
    
#             if mn_n!=1e9:
#                 print(mn_n)
#             else:
#                 print(-1)

#         elif x==-1:
            
#             mx_n = -1

#             for a in range(l,0,-1):

#                 while rec3[-a] and -rec3[-a][0] in solved_set:
#                     heapq.heappop(rec3[-a])


#                 # while rec3[-a] and -rec3[-a][0] in solved \
#                 #     and a in solved[-rec3[-a][0]]:
#                 #     heapq.heappop(rec3[-a])

#                 if rec3[-a]:
#                     mx_n= -rec3[-a][0]
#                     break

#             if mx_n!=-1:
#                 print(mx_n)
#             else:
#                 print(-1)


#     elif o=='add':
#         p,l,g = map(int,con)

#         # rec1
#         heapq.heappush(rec1[g],(-l,-p))
#         heapq.heappush(rec1[-g],(l,p))

#         # rec2
#         heapq.heappush(rec2_h,(-l,-p))
#         heapq.heappush(rec2_e,(l,p))

#         # rec3
#         heapq.heappush(rec3[l],p)
#         heapq.heappush(rec3[-l],-p)

#         p2l[p]=l

#         # remove
#         # 같은 번호 + 같은 난이도가 있다면 remove
#         if p in solved_set:
#             solved_set.remove(l)

#         # if p in solved and l in solved[p]:

#         #     solved[p].remove(l)


#     elif o=='solved':
#         p = int(con[0])
#         l = p2l[p]
#         solved_set.add(p)
#         # solved[p].add(l)

