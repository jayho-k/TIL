'''
max heap 구현
1) heapify down
2) make heap
3) insert
4) delete
5) heapify up 

heapq를 이용해서 min, max heap만들기
'''

from heapq import heapify
class Heap:

    def __init__(self, L=[]):
        self.lst = L
        self.make_heap()

    def __str__(self):
        return str(self.lst)

    def heapify_down(self, k, n):
        if n == 0:
            return
        else:
            while 2*k+1<n: # 이부분
                m = k
                l,r = 2*k+1, 2*k+2
                if self.lst[l] > self.lst[m]:
                    m =l

                if r < n and self.lst[r] > self.lst[m]:
                    m=r
                
                if m != k:
                    self.lst[k], self.lst[m] =self.lst[m],self.lst[k]
                    k=m
                else:
                    break

    def heapify_up(self,k):
        # 아래서 부터 = 부모노드를 찾아줘야함
        p = (k-1)//2
        if self.lst[p] < self.lst[k]:
            self.lst[p],self.lst[k] = self.lst[k],self.lst[p]
        
    def make_heap(self):
        # heapify_down + for문이 필요하다
        n = len(self.lst)

        # 밑에부터 가는 이유 => 큰값이 위로 올라가기 때문이다
        for k in range(n//2,-1,-1):
            self.heapify_down(k,n)
            print(k)

    def insert():
        pass

    def delete():
        pass

lst = [1,2,3,4,5,6,7,8,9,10]

hlst = Heap(lst)
print(hlst)
