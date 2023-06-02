"""
요구사항
 - 


"""



"""
우선순위
 1. a 가 가장 작은 class
 2. b + c가 가장 작은 class
 3. b가 가장 장은 class
 4. c가 가장 장은 class

"""
import heapq
class Compare:
    def __init__(self,a,b,c,d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        
    # 즉 < 부호가 사용되면 이러한 매커니즘이 돌아가게 된다는 뜻이다.
    def __lt__(self,other):

        if self.a != other.a:
            print("self.a < other.a ",self.a < other.a, self.a, other.a)
            return self.a < other.a
        
        if self.b+self.c != other.b+other.c:
            print("self.b+self.c != other.b+other.c ",self.b+self.c != other.b+other.c\
                  , self.b+self.c, other.b+other.c)
            return self.b+self.c < other.b+other.c
         
        if self.b != other.b:
            print("self.b != other.b",self.b != other.b, self.b, other.b)
            return self.a < other.b
        
        if self.c != other.c:
            print("self.c != other.c",self.c != other.c, self.c, other.c)
            return self.a < other.b

c1 = Compare(4,2,3,4)
c2 = Compare(2,2,3,4)
c3 = Compare(2,3,3,4)
c4 = Compare(1,2,3,4)

q = []
print("c1")
heapq.heappush(q,c1)
print()
print("c2")
heapq.heappush(q,c2)
print()
print("c3")
heapq.heappush(q,c3)
print()
print("c4")
heapq.heappush(q,c4)
print()

for _ in range(4):
    c = heapq.heappop(q)
    print(c.a,c.b,c.c,c.d)
