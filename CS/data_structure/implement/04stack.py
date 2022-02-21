'''
stack
    ==> 넣고 빼는 기능
    ==> 추가로 개수, 가장위에 있는 값이 추가 될 수 있다

1. init
    list를 만들어 주어야 한다
2. push
    넣는다
3. pop
    뺀다
4. top
    위에 있는 수를 가장 마지막 수를 찾는다
5. len
    길이를 센다.
'''

class Stack:

    def __init__(self):
        # self.size = size
        # self.top = -1
        self.items = []

    def push(self, var):
        self.items.append(var)

    def pop(self):
        try:
            return self.items.pop()

        except (IndexError):
            print('Empty')

    def top(self):
        return self.items[-1]

    def __len__(self):
        cnt = 0
        for _ in self.items:
            cnt += 1

        return cnt

    # def __str__(self):
    #     return self.items


a = Stack()
print(a)

a.push(3)
a.push(4)
a.push(8)
print(a.items)

a.pop()
print(a.items)

print(a.__len__())

print(a.top())

print(a.pop())
a.pop()
a.pop()
