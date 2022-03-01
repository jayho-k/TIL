# Queue

FIFO: 먼저 들어온 것이 먼저 나감

큐에서는 enqueue라고 한다 (stack 에 push 같은 것) ==> append라고 생각하면 됨

큐에서는 dequeue라고 한다 (stack에서 pop같은 것) ==> 다음에 dequeue되는 값을 알아야한다

==> class queue:

```python
class Queue:
    def __init__(self):
        self.items = []
        self.front_idx = 0
    
    def enqueue(self, val):
        self.items.append(val)
        
    def dequeue(self):
        if self.fron_idx == len(self.items):
            print("Q is empty")
            return None
        else:
            x = self.items[front_idx]
            self.front_index += 1
            return x
  
```



예시) Josephis problem

n = 6, k = 2 (1번부터 6번까지 동그랗게 앉음) k => 2번째 사람이 계속해서 죽는 것

```python


```



- deque 클라스를 제공한다
  - appendleft
  - popleft

```python
# 이런식으로 사용한다.
from collections import deque

a = [10,20,30,40,50]
d = deque(a)

d.append(100)
d.appendleft(1000)
tmep = d.pop()
# temp의 100의 값이 저장된다

tmep = d.popleft()


d.rotate(2)
d
# 두칸을 회전시킨다

d.rotate(-1)
d
```































