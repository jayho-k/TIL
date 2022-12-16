'''
4 4
4 3 2 1
3 1 2 1
'''

import heapq
ans = 1
n,m = map(int,input().split())
box = [-x for x in map(int,input().split())]
child = list(map(int,input().split()))
heapq.heapify(box)

for c in child:
    b = -heapq.heappop(box)
    
    if b >= c:
        heapq.heappush(box,c-b)

    else:
        ans = 0
        break

print(ans)

        
    

