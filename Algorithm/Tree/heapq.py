
# heapq 는 최소 힙만 사용함
import heapq
lst = [6,2,1,3,7,2,4]

heapq.heapify(lst)
print(lst)

#그렇기 때문에 이러한 방법으로 max heap을 구현해준다
mx_heap = [(-i,i) for i in lst]

heapq.heapify(mx_heap)
print(mx_heap)