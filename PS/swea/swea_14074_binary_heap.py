'''
1
8
18 57 11 52 14 45 63 40

'''

import heapq

def search(last_i,v):
    if last_i == 0:
        print(f'#{tc} {v}')
        return

    search(last_i//2, v+h[last_i//2])


T = int(input())
for tc in range(1,T+1):

    n = int(input())
    lst = list(map(int,input().split()))

    h = []
    for l in lst:
        heapq.heappush(h,l)

    h = [0]+h
    search(n,0)


