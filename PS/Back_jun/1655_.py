'''

7
1
5
2
10
-99
7
5

'''
import sys
import heapq

n = int(input())
input = sys.stdin.readline
max_heap = []
min_heap = []
ans = []
for _ in range(n):
    a = int(input())
    if len(max_heap) == len(min_heap):
        heapq.heappush(max_heap,-a)

    else:
        heapq.heappush(min_heap,a)

    if min_heap and (-max_heap[0]>min_heap[0]):
        l = heapq.heappop(max_heap)
        r = heapq.heappop(min_heap)
        heapq.heappush(max_heap,-r)
        heapq.heappush(min_heap,-l)

    print(-max_heap[0])




# n = int(input())
# import sys
# input = sys.stdin.readline
# tmp = []
# tmp_set = set()
# for _ in range(n):
#     a = int(input())
#     # if a not in tmp_set:
#     tmp_set.add(a)
#     tmp.append(a)
#     tmp.sort()
#     # print(tmp,' and ',len(tmp)//2)
#     if len(tmp)%2:
#         print(tmp[len(tmp)//2])
        
#     else:
#         print(tmp[(len(tmp)//2)-1])

#     # else:
#     #     if len(tmp)%2:
#     #         print(tmp[len(tmp)//2])
            
#     #     else:
#     #         print(tmp[(len(tmp)//2)-1])







# import heapq
# import sys
# input = sys.stdin.readline
# n = int(input())

# tmp = []
# for _ in range(n):
#     max_heap = []
#     min_heap = []
#     a = int(input())
#     tmp.append(a)
#     for i in range(len(tmp)):
#         heapq.heappush(max_heap,-tmp[i])
#         heapq.heappush(min_heap,tmp[i])
    
#     # 홀수
#     if len(tmp)%2:
#         while 1:                
#             mx = heapq.heappop(max_heap)
#             mn = heapq.heappop(min_heap)
#             if -mx==mn:
#                 print(mn)
#                 break

#     else:

#         heapq.heappush(max_heap,1e9)
#         heapq.heappush(min_heap,-1e9)
#         # print(max_heap)
#         # print(min_heap)
#         while 1:
#             mx = heapq.heappop(max_heap)
#             mn = heapq.heappop(min_heap)
#             if -mx==mn:
#                 print(mn)
#                 break


    
