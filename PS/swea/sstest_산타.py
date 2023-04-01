class Node:
    def __init__(self,key=None):
        self.key = key
        self.prev = None
        self.next = None
        

class d_linked_lst:

    def __init__(self):
        self.head = self
        self.tail = self
        self.size = 0

    def findSize(self):
        return self.size

    def addFront(self,key):
        if self.size==0:
            self.head = Node(key)
            self.tail = self.head
            self.size+=1

        else:
            # node <-> head
            node = Node(key)
            self.head.prev = node
            node.next = self.head
            self.head = node
            self.size+=1

    def addBack(self,key):
        if self.size==0:
            self.head = Node(key)
            self.tail = self.head
            self.size+=1
        else:
            # tail <-> node
            node = Node(key)
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
            self.size+=1

    def checkFront(self):
        return self.head.key

    def popFront(self):
        if self.size ==0:
            return None
        node = self.head
        self.head = node.next
        # self.head.prev = None
        self.size-=1
        return node.key
    
    def popBack(self):
        if self.size==0:
            return None
        node = self.tail
        self.tail = node.prev
        # self.tail.next = None
        self.size-=1
        return node.key

    def remove(self,id):
        if self.size==0:
            return None
        
        if self.head.key[0]==id:
            ans_id,_ = self.popFront()
            return ans_id
        
        elif self.tail.key[0]==id:
            ans_id,_ = self.popBack()
            return ans_id
        
        else:
            node = self.head
            for _ in range(self.size):
                if node.key[0]==id:
                    # prev  id_node  next
                    prev_node = node.prev
                    next_node = node.next

                    prev_node.next = next_node
                    next_node.prev = prev_node
                    
                    # node.next = None
                    # node.prev = None
                    self.size-=1
                    return node.key[0]
                node = node.next
    
    def checkBox(self,id):
        if self.size==0:
            return None

        if self.head.key[0]==id:
            return self.head.key[0]
        
        else:
            node = self.head
            for _ in range(self.size):
                if node.key[0]==id:
                    # node~tail head prev_node
                    self.tail.next = self.head
                    self.head.prev = self.tail
                    
                    prev_node = node.prev
                    # prev_node.next = None

                    self.tail = prev_node
                    self.head = node
                    # self.head.prev = None
                    
                    return  node.key[0]
                node = node.next

    def together(self,dlst):

        self.tail.next = dlst.head
        dlst.head.prev = self.tail
        self.tail = dlst.tail
        self.size+= dlst.findSize()


    def check(self):

        lst = []
        node = self.head
        for _ in range(self.size):
            lst.append(node.key)
            node = node.next
        return lst


q = int(input())
for _ in range(q):
    
    order,*tmp = map(int,input().split())
    
    if order==100:
        n,m,*ids_weights = tmp
        ids = ids_weights[:len(ids_weights)//2]
        weights = ids_weights[len(ids_weights)//2:]
        belts = {}
        belts_set = {}
        broken = [0]*m

        b_n = 0
        for i in range(0,n,n//m):
            # 생성
            dlst = d_linked_lst()
            belts[b_n] = dlst
            belts_set[b_n] = set()
            for j in range(i,i+n//m):
                # add
                belts[b_n].addBack((ids[j],weights[j]))
                belts_set[b_n].add(ids[j])                
            b_n+=1
    
    elif order==200:
        mx = tmp[0]
        total = 0
        for i2 in range(m):
            if belts[i2].findSize()==0 or broken[i2]:
                continue 
            
            else:
                if belts[i2].checkFront()[1]<=mx:
                    i2_id,i2_w = belts[i2].popFront()
                    belts_set[i2].remove(i2_id)
                    total+=i2_w
                else:
                    i2_id,i2_w = belts[i2].popFront()
                    belts[i2].addBack((i2_id,i2_w))

        # print('order 200 : ', total)
        print(total)

    
    elif order==300:
        r_id = tmp[0]
        for i3 in range(m):
            if r_id in belts_set[i3]:
                belts_set[i3].remove(r_id)
                # print('order 300 :', belts[i3].remove(r_id))
                print(belts[i3].remove(r_id))
                # print(belts[i3].check())
                break
        else:
            # print('order 300 :', -1)
            print(-1)


    elif order==400:
        f_id = tmp[0]
        for i4 in range(m):
            if f_id in belts_set[i4]:
                belts[i4].checkBox(f_id)
                # print('order 400 :', i4+1)
                print(i4+1)
                break
        else:
            print(-1)
            # print('order 400 :', -1)


    elif order==500:
        b_num = tmp[0]


        if belts[b_num-1].findSize()==0 or broken[b_num-1]:
            print(-1)

        else:
            for i5 in range(m-1):
                if (belts[(i5+b_num)%m].findSize()==0) or broken[(i5+b_num)%m]:
                    continue

                else:
                    belts[(i5+b_num)%m].together(belts[b_num-1])
                    broken[b_num-1]=1
                    belts_set[(i5+b_num)%m]=belts_set[(i5+b_num)%m] | belts_set[b_num-1]
                    belts_set[b_num-1] = set()
                    print(b_num)
                    break

'''
12
100 12 3 10 12 20 15 14 19 22 25 16 17 21 18 30 30 20 20 10 18 17 15 25 11 14 17
200 25
300 22
300 999
400 14
400 18
500 3
200 5
300 12
500 1
500 3
200 40

35
22
-1
-1
3
3
0
12
1
-1
15


'''
# dlst = d_linked_lst()
# dlst.addBack((1,0))
# dlst.addBack((2,0))
# dlst.addBack((3,0))
# dlst.addFront((0,0))
# print(dlst.check())
# dlst.checkBox(2)
# print(dlst.check())

# dlst2=d_linked_lst()
# dlst2.addBack((100,0))
# dlst2.addBack((2,0))
# dlst2.addBack((3,0))
# dlst.together(dlst2)
# print(dlst.check())

'''
35
22
-1
-1
3
3
0
12
1
-1
15


Traceback (most recent call last):
File "Main.py", line 177, in <module>
i2_id,i2_w = belts[i2].popFront()
File "Main.py", line 54, in popFront
next_node.prev = None
AttributeError: 'NoneType' object has no attribute 'prev'


Traceback (most recent call last):
File "Main.py", line 172, in <module>
if belts[i2].checkFront()[1]<=mx:
TypeError: 'int' object is not subscriptable (key 1)



'''