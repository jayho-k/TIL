'''
3
1 3
2 4
3 5

5
20 23
17 20
23 24
4 14
8 18

10
14 23
2 19
1 22
12 24
21 23
6 15
20 24
1 4
6 15
15 16

15
18 19
2 7
11 15
13 16
23 24
2 14
13 22
20 23
13 19
7 15
5 21
20 24
16 22
17 21
9 24
'''
import heapq
from collections import deque


n = int(input())
lst = []
end = []

for _ in range(n):
    s = list(map(int,input().split()))
    lst.append(s)
    heapq.heappush(end,s[1])

lst.sort()
# 끝나는 시간을 다 넣는다.


cnt = 1
for i in range(1,n):
    # 겹치는걸 찾는거야 ==> 그게 강의실 하나 더 써야한다는 뜻이니깐
    # 즉 지금강의 끝나는 시간보다 다음강의 시작시간이 더 작아? ==> 그럼 시간 겹친다는 뜻
    # 6,15 와 15,16은 안겹친다 그럼 이 둘은 하나로 합쳐주면 된다 즉 : 6,15   15,16  ==> 6,16

    # 겹쳐
    if end[0] > lst[i][0]:
        cnt += 1

    # 안겹쳐
    else:
        heapq.heappop(end)

print(lst)
print(cnt)
    


# n = int(input())

# lst = [list(map(int,input().split())) for _ in range(n)]
# lst.sort(reverse=True)
# # print(lst)
# cnt = 0
# end = 0
# while lst:

#     for i in range(n-1,-1,-1):
#         if end <= lst[i][0]:
#             end = lst[i][1]
#             lst.pop(i)

#     n = len(lst)
#     end = 0
#     cnt += 1
        
# print(cnt)