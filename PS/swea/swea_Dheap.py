'''

'''
import heapq

T = int(input())
for tc in range(1,T+1):
    n = int(input())
    lst = list(map(int, input().split()))
    heap = []
    for i in lst:
        heapq.heappush(heap,i)

    heap = [0]+heap
    # 맨 끝의 부모는 나누기 2를 하면 부모의 인덱스가 나온다
    total = 0
    c = len(heap)-1

    while 1:
        p = c//2
        total += heap[p]
        c = p

        if c == 1:
            break

    print(f'#{tc} {total}')