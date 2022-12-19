'''

10 15 35

'''
def bfs(a,b):

    q = deque([(a,b)])

    while q:
        a,b = q.popleft()
        c = total-a-b
        if a == b == c:
            return 1
        
        for small_group in [[a,b],[b,c],[c,a]]:
            small_group.sort()
            small = small_group[0]
            large = small_group[1]
            new_a = small*2
            new_b = large-small
            if new_a > 0 and new_b > 0 and (new_a,new_b) not in visited:
                q.append((new_a,new_b))
                visited.add((new_a,new_b))
                visited.add((new_b,new_a))
            
    return 0

from collections import deque
a,b,c = map(int,input().split())
total = a+b+c
visited = set()

if total%3:
    print(0)
else:
    print(bfs(a,b))