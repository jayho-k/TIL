'''
max heap 구현
1) heapify down
2) make heap
3) insert
4) delete
5) heapify up 

heapq를 이용해서 min, max heap만들기
'''

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
            while 2*k+1<n: # 왼쪽 자식노드가 n보다 작을때
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
        while k>0 and self.lst[p] < self.lst[k]: #k가 0보다 같거나 작다는 뜻 = 루트노드
            self.lst[p],self.lst[k] = self.lst[k],self.lst[p]
            print(self.lst)
            k = p
            # p = k
        
    def make_heap(self):
        # heapify_down + for문이 필요하다
        n = len(self.lst)

        # 밑에부터 가는 이유 => 큰값이 위로 올라가기 때문이다
        for k in range(n//2,-1,-1):
            self.heapify_down(k,n)
            # print(k)

    def insert(self, key):
        self.lst.append(key)
        self.heapify_up(len(self.lst)-1)
        

    def max_delete(self):
        key = self.lst[0]
        self.lst[0],self.lst[-1] = self.lst[-1],self.lst[0]
        self.lst.pop()
        self.heapify_down(0,len(self.lst))
        return key


lst = [1,2,3,4,5,6,7,8,9,10]

hlst = Heap(lst)
<<<<<<< HEAD

print(1)
=======
print(hlst)

hlst.insert(0)
hlst.insert(2)
print(hlst)

hlst.max_delete()
print(hlst)
>>>>>>> cb5c229d1969c607168e5e8aca56df03d8f210c4
