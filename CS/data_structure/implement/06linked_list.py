'''
한방향(single)
특징
1. head node를 따라간다
2. 하나의 노드에 2개의 주소를 가지고 있다

3 -> 9 -> -1 안 한방향을 만들어보자

노드
1. 노드생성(key, next) ==> 특징 2

링크드 리스트
1. 생성
    헤드노드, 사이즈

2. pushFront
    1) 새로운 노드 생성
    2) new 다음 = 전에 있던 head
    3) new가 새로운 head가 됨
    4) size += 1

3. pushBack
    1) 새로운 노드 생성
    2) 문제점: 맨 끝에 아이를 찾아줘야함
        tail을 처음 head로 잡아주고 시작
        2-1) while문으로 다음이 None인 아이를 찾아줘야함
        2-2) 찾으면 걔를 tail이라고 했을 떄 tail 다음 = new
    3) if len(self) == 0(self.size = 0)이면 걔가 head

4. popFront
    ==> 모든지 삭제할 떄 주의할점
    ==> 그 값이 없을 수 있다라는 점을 확인해줘야한다.
    1) 원래 head의 다음이 head가 됨
    2) 원래 헤드는 없어짐
    3) size -= 1
    4) 삭제한 값 return 해줌

5. popBack

    이때 prev와 tail 두가지로 간다
    하지만 len ==1일 경우 prev값이 나올 수 없음
    따라서 len == 1일 겨우에는 head는 None으로 하여 값을 없애버린다


    ==> 마찬가지로 그 값이 없을수 있다는 것을 확인
    1) prev,tail 값을 저장하면서 간다 None, head 초기값
    2) tail 값을 찾는다
    3) tail값을 삭제
    4) prev가 tail 값이 된다.
    5) size -= 1
    6) 삭제한 값 보여줌

6. __len__

7. search
    1. 찾고 싶은것을 찾았을 때
    2. 못찾았을때


8. generator
'''
# 노드 생성
class Node:
    
    def __init__(self, key= None):
        self.key = key
        self.next = None

    def __str__(self):
        return str(self.key)

# a = Node(3)
# b = Node(9)
# c = Node(-1)
# a.next = b
# b.next = c

class SingleLinkedList:

    def __init__(self):
        self.head = None
        self.size = 0

    def pushFront(self, key):
        new_node = Node(key)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def pushBack(self, key):
        new = Node(key)

        if self.size == 0:
            self.head = new

        else: # 새로운 노드가 tail로 가주어야 함/ tail을 찾아야하고/ 그전에 초기화 해줘야함
            tail = self.head
            while tail.next != None:
                tail = tail.next
            
            tail.next = new
            self.size += 1

    def popFront(self): # 맨 앞에 값 삭제
        if self.size == 0:
            return None

        else:
            de = self.head
            de_key = de.key
            self.head = de.next
            del de
            self.size -= 1

            return de_key

    def popBack(self):
        if self.size == 0:
            return None

        elif self.size == 1:
            self.head = None
            self.size -= 1
            return self.head

        else:
            # prev값과 tail값을 동시에 저장하면서 가주어야 한다.
            # tail = 삭제, prev값 = tail
            # 초기화
            prev, tail = None, self.head
            while tail.next != None:
                prev = tail
                tail = tail.next

            prev.next = None
            key = tail.key
            del tail
            return key

    def search(self, key):
        var = self.head
        # print(type(var)) # 타입이 __main__.Node이다 따라서 int 값이 아니기 때문에 key와 비교를 해주어야함
        # print(type(var.key)) # 타입이 int값이다

        location = 0
        while var != None:
            if var.key == key: # 주의할점은 var의 키값과 비교를 해주어야 한다. 
                print('location' , location)
                return var
            var = var.next
            location += 1
        # 못찾음
        return None

    def get_node(self, index):
        cnt = 0
        lst = self.__iterator__()
        for i in lst:
            if cnt == index:
                return i

            cnt += 1
            
    
    def insert(self, index, node):
        new = Node(node) # 새로운 값
        prev = self.get_node(index-1) # 지정한 곳의 전 값
        new.next = prev.next
        prev.next = new
        



    def __iterator__(self):
        var = self.head
        while var != None:
            yield var
            var = var.next
        return





    
s = SingleLinkedList()
s.pushFront(4)
s.pushFront(1)
s.pushFront(9)
s.pushFront(7)
s.pushFront(3)
print('s.pushFront(3)')
print('size', s.size)
print('head', s.head)
print('-'*30)

s.pushBack(7)
print('s.pushBack(7)')
print('size', s.size)
print('head', s.head)
print('tail', s.head.next)
print('-'*30)

s.pushBack(8)
print('s.pushBack(8)')
print('size', s.size)
print('head', s.head)
print('-'*30)


sch = s.search(8)
print('s.search(8)')
print('size', s.size)
print('key',sch)
print('-'*30)

lst = s.__iterator__()
for i in lst:
    print(i)

print('-'*30)
print('s.get_node(4)')
print(s.get_node(4))

print('-'*30)
print('s.insert(4,10)')
lst = s.__iterator__()
for i in lst:
    print(i)



# lst = s.__iterator__()
# for i in lst:
#     print(i)


# insert(self, var ,key):


# print(s.popFront())
# print('popFront')
# print('size', s.size)
# print('head', s.head)
# print('-'*30)


# print(s.popBack())
# print('popBack')
# print('size', s.size)
# print('head', s.head)
# print('-'*30)
