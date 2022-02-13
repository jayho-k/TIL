'''
queue 구현

1. init
    : 리스트 생성

2. enqueue
    : 뒤에다가 넣는다

3. dequeue
    앞에 값을 리턴하고 빠진다

4. len
    길이가 몇인지

5. bottom
    : 밑에 값이 무엇인지 보여준다
'''

class Queue:

    def __init__(self):
        self.items = []

    def enqueue(self, var):
        self.items.append(var)

    def dequeue(self):

        try:
            return self.items.pop(0)

        except (IndexError):
            print('Empty')

    
    def __len__(self):
        return len(self.items)
    
    def bottom(self):
        return self.items[0]

q = Queue()
q.enqueue(3)
q.enqueue(3)
q.enqueue(3)
q.enqueue(3)
q.enqueue(3)
print(q.items)

q.dequeue()
q.dequeue()
q.dequeue()
q.dequeue()
print(q.items)

print(q.dequeue())
print(q.items)
q.dequeue()