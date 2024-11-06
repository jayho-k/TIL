"""

6
1 2 3 1 2 1

5
1 1 1 1 1

5
3 1 1 1 1

5
1 1 1 1 3
"""

def init(n):
    dic = {}
    memoi = 0
    for i in range(1,n+1):
        memoi += i
        dic[i] = memoi
    return dic

def calculation(lastCal,front,back):

    length = back-front

    if lastCal == -1:
        return dic[length]

    if lastCal >= front:
        return dic[length] - dic[length - (back-1-lastCal)]
    
    elif lastCal < front:
        return dic[length]
        

def cal():

    sumAns = 0
    lastCal = -1
    end = 0

    duplSet = set()

    for start in range(n):

        # 중복이 안되고 end가 < n일 때
        while lst[end] not in duplSet and end < n:
            duplSet.add(lst[end])
            end += 1
            
            if end == n:
                sumAns += calculation(lastCal,start,end)
                return sumAns
        
        sumAns += calculation(lastCal,start,end)
        lastCal = end-1
        duplSet.remove(lst[start])

n = int(input())
lst = list(map(int,input().split()))
dic = init(n)

duplSet = set()
print(cal())










# # two pointer
# for front in range(n):
#     flag1 = False
#     # dupl check
#     # dup o => x+=1 [front +=1 ]
#     # dup x => add 
#     if checkDupl(front):
#         continue

#     duplSet.add(lst[front])

#     while True:
#         if back == n: # last
#             print(duplSet,1)
#             # calc
#             break
#         if checkDupl(back):
#             flag1 = True
#             print(duplSet,2)
#             # calc
#             break
        
#         duplSet.add(lst[back])
#         back += 1

#     if flag1: continue
    
#     duplSet.remove(lst[front])





















# """

# 6
# 1 2 3 1 2 1

# 5
# 1 1 1 1 1

# 5
# 1 1 1 1 3
# """
# from collections import deque
# def init(n):
#     dic = {}
#     memoi = 0
#     for i in range(1,n+1):
#         memoi += i
#         dic[i] = memoi
#     return dic

# def checkDupl(x):
#     if lst[x] in duplSet:
#         return True
#     return False

# def calculation(lastCal,front,back):
#     length = back-front

#     if lastCal == -1 or length == 1:
#         return dic[length]

#     if lastCal >= front:
#         return dic[length] - dic[length - (back-1-lastCal)]
    
#     elif lastCal < front:
#         return dic[length]
        

# def cal():
#     sumAns = 0
#     lastCal = -1
#     back = 1

#     duplSet = set()

#     for front in range(n):

#         while True:
#             if back == n:
#                 sumAns += calculation(lastCal, front, back)
#                 return sumAns
                
#             if lst[front] == lst[back]:

#                 sumAns += calculation(lastCal, front,back)

#                 lastCal = back-1         
#                 back+=1
#                 break
#             back += 1

#     return sumAns


# n = int(input())
# lst = list(map(int,input().split()))
# dic = init(n)

# duplSet = set()
# q = deque()
# print(cal())










# # # two pointer
# # for front in range(n):
# #     flag1 = False
# #     # dupl check
# #     # dup o => x+=1 [front +=1 ]
# #     # dup x => add 
# #     if checkDupl(front):
# #         continue

# #     duplSet.add(lst[front])

# #     while True:
# #         if back == n: # last
# #             print(duplSet,1)
# #             # calc
# #             break
# #         if checkDupl(back):
# #             flag1 = True
# #             print(duplSet,2)
# #             # calc
# #             break
        
# #         duplSet.add(lst[back])
# #         back += 1

# #     if flag1: continue
    
# #     duplSet.remove(lst[front])







