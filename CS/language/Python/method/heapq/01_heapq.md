# 01_heapq



## heappush

```python
def heappush(heap, item):
    """Push item onto heap, maintaining the heap invariant."""
    # heap에 item을 넣고 _shiftdown 진행
    heap.append(item)
    _siftdown(heap, 0, len(heap)-1)
```



**shiftdown**

```python
def _siftdown(heap, startpos, pos):
    newitem = heap[pos] # pos끝 부분 => 새로운 값
    
    # 처음 : pos = len(heap)-1 > startpos = 0
    while pos > startpos:
        # 그 위에 parent  //  2*k, 2*k+1 ==> 자식
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        
        # 새로운 값이 더 작으면
        # heap[새로우 값위 치] => parent값,
        # 새로운값 위치 = 부모 위치 
        if newitem < parent:
            heap[pos] = parent
            pos = parentpos
            continue
        break
    heap[pos] = newitem
```



## lt, gt 

```python
class Compare:

    def __init__(self, item):
        self.item = item
        
    
    def __lt__(self, other):
        return self.item < other.item
    
    def __gt__(self, other):
        return self.item > other.item
    	
        # 만약 부호를 바꾼다면
        return self.item < other.item 
    
    
c1 = Compare(2)
c2 = Compare(3)

print(c1>c2) ==> False
print(c1<c2) ==> True

# 만약 부호를 바꾼다면 
print(c1>c2) ==> False가 아니라 True가 나오게 된다.
```

- lt를 활용하여 heap을 커스텀 할 수 있음



## heap coustom

- 우선 순위 큐로 사용할 경우 여러가지 조건을 맞춰 주어야 할 때가 있다. 따라서 이때 **\__lt__ 를 활용**하여 해결할 수 있음

```python
"""
요구사항
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
    # shiftdown에서 < 부호가 사용된다. 
    # ==> 즉 < 부호가 사용될 때마다 밑에 있는 로직이 돌게 된다.
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

    
    
"""
결과
c1

c2
self.a < other.a  True 2 4

c3
self.b+self.c != other.b+other.c  True 6 5

c4
self.a < other.a  True 1 4
self.a < other.a  True 1 2

self.b+self.c != other.b+other.c  True 5 6
self.a < other.a  False 4 2
1 2 3 4
self.a < other.a  True 2 4
2 2 3 4
2 3 3 4
4 2 3 4

"""
```

- 위와 같은 방식으로 priority queue를 구현할 수 있다.

















