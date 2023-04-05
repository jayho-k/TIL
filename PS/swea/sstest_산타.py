'''
7
100 12 3 10 12 20 15 14 19 22 25 16 17 21 18 30 30 20 20 10 18 17 15 25 11 14 17
200 25
300 22
300 999
400 14
400 18
500 3
'''

from collections import defaultdict

MAX_M = 10

# 변수 선언
n, m, q = -1, -1, -1

# 각 id별로 상자 무게를 저장합니다.
weight = {}

# id에 해당하는 상자의 nxt값과 prv값을 관리합니다.
# 0이면 없다는 뜻입니다.
prv, nxt = defaultdict(lambda: 0), defaultdict(lambda: 0)

# 각 벨트별로 head, tail id를 관리합니다.
# 0이면 없다는 뜻입니다.
head = [0] * MAX_M
tail = [0] * MAX_M

# 벨트가 망가졌는지를 표시합니다.
broken = [False] * MAX_M

# 물건 별로 벨트 번호를 기입합니다.
# 벨트 번호가 -1이면 사라진 것입니다.
belt_num = defaultdict(lambda: -1)


# 공장 설립
def build_factory(elems):
    global n, m
    
    # 공장 정보를 입력받습니다.
    n, m = elems[1], elems[2]
    ids, ws = elems[3:3+n], elems[3+n:3+n+n]
    
    # id마다 무게를 관리합니다.
    for i in range(n):
        weight[ids[i]] = ws[i]
    
    # 벨트 별로 상자 목록을 넣어줍니다.
    size = n // m
    for i in range(m):
        # head, tail을 설정해줍니다.
        head[i] = ids[i * size]
        tail[i] = ids[(i + 1) * size - 1]
        for j in range(i * size, (i + 1) * size):
            # 상자 ID마다 벨트 번호를 기입합니다.
            belt_num[ids[j]] = i

            # nxt, prv를 설정해줍니다.
            if j < (i + 1) * size - 1:
                nxt[ids[j]] = ids[j + 1]
                prv[ids[j + 1]] = ids[j]


# Id에 해당하는 상자를 삭제합니다
def remove_id(_id, remove_belt):
    b_num = belt_num[_id]
    # 벨트 번호를 제거해줍니다.
    if remove_belt:
        belt_num[_id] = -1

    # 하나 남은 원소라면
    # head, tail이 사라지고 끝납니다.
    if head[b_num] == tail[b_num]:
        head[b_num] = tail[b_num] = 0

    # 삭제 되는게 head라면
    # head만 변경되고 끝납니다.
    elif _id == head[b_num]:
        nid = nxt[_id]
        head[b_num] = nid
        prv[nid] = 0
    # 삭제 되는게 tail이라면
    # tail만 변경되고 끝납니다.
    elif _id == tail[b_num]:
        pid = prv[_id]
        tail[b_num] = pid
        nxt[pid] = 0
    # 중간에 있는 id가 삭제되는 것이라면
    # nxt, prv만 수선해줍니다.
    else:
        pid, nid = prv[_id], nxt[_id]
        nxt[pid] = nid
        prv[nid] = pid

    # nxt, prv값을 지워줍니다.
    nxt[_id] = prv[_id] = 0


# target_id 바로 뒤에
# id를 추가합니다.
def push_id(target_id, _id):
    nxt[target_id] = _id
    prv[_id] = target_id

    # 만약 target_id가 tail이었다면
    # tail을 변경해줍니다.
    b_num = belt_num[target_id]
    if tail[b_num] == target_id:
        tail[b_num] = _id


# 물건 하차
def drop_off(elems):
    w_max = elems[1]
    
    # 각 벨트마다 보며
    # 첫 번째 상자를 열어봅니다.
    w_sum = 0
    for i in range(m):
        # 망가진 벨트라면 넘어갑니다.
        if broken[i]:
            continue

        # 벨트의 head를 확인합니다.
        if head[i] != 0:
            _id = head[i]
            w = weight[_id]

            # 가장 앞에 있는 상자의 무게가 w_max 이하라면
            # 하차시키고 답에 더해줍니다.
            if w <= w_max:
                w_sum += w

                # 하차를 진행합니다.
                remove_id(_id, True)
            # 그렇지 않다면
            # 상자를 맨 뒤로 올려줍니다.
            elif nxt[_id] != 0:
                # 제거해준 뒤
                remove_id(_id, False)
                
                # 맨 뒤에 push해줍니다.
                push_id(tail[i], _id)

    # 하차한 상자의 무게 합을 출력합니다.
    print(w_sum)


# 물건 제거
def remove(elems):
    r_id = elems[1]

    # 이미 삭제된 상자라면
    # -1을 출력하고 패스합니다.
    if belt_num[r_id] == -1:
        print(-1)
        return
        
    # 해당 상자를 제거합니다.

    remove_id(r_id, True)
    print(r_id)
    

# 물건 확인
def find(elems):
    f_id = elems[1]

    # 이미 삭제된 상자라면
    # -1을 출력하고 패스합니다.
    if belt_num[f_id] == -1:
        print(-1)
        return

    # 해당 상자를 찾아
    # 이를 맨 앞으로 당겨줍니다.
    # head가 아닌 경우에만 유효합니다.
    b_num = belt_num[f_id]
    if head[b_num] != f_id:
        orig_tail = tail[b_num]
        orig_head = head[b_num]

        # 새로 tail을 갱신해줍니다.
        now_tail = prv[f_id]
        tail[b_num] = now_tail
        nxt[now_tail] = 0

        # 기존 tail의 nxt를 head로,
        # heda의 prv를 기존 tail로 만들어줍니다.
        nxt[orig_tail] = orig_head
        prv[orig_head] = orig_tail

        # 새로 head를 지정합니다.
        head[b_num] = f_id

    # 해당 ID의 belt 번호를 출력합니다.
    print(b_num + 1)


# 벨트 고장
def broken_belt(elems):
    b_num = elems[1]
    b_num -= 1

    # 이미 망가져 있다면
    # -1을 출력하고 패스합니다.
    if broken[b_num]:
        print(-1)
        return

    broken[b_num] = 1

    # 만약 빈 벨트라면 패스합니다.
    if head[b_num] == 0:
        print(b_num + 1)
        return

    # 오른쪽으로 돌면서
    # 아직 망가지지 않은 벨트 위로 상자를 전부 옮겨줍니다.
    nxt_num = b_num
    while True:
        nxt_num = (nxt_num + 1) % m
        # 최초로 망가지지 않은 곳이 보이면
        if not broken[nxt_num]:
            # 만약 해당 벨트가 비어있다면
            # 그대로 옮겨줍니다.
            if tail[nxt_num] == 0:
                head[nxt_num] = head[b_num]
                tail[nxt_num] = tail[b_num]
            else:
                # 해당 위치로 상자를 전부 옮겨줍니다.
                # head만 tail뒤에 붙여준 뒤
                push_id(tail[nxt_num], head[b_num])
                # tail만 갈아껴주면 됩니다.
                tail[nxt_num] = tail[b_num]

            # head부터 tail까지 보며
            # belt_num을 갱신해줍니다.
            _id = head[b_num]
            while _id != 0:
                belt_num[_id] = nxt_num
                _id = nxt[_id]

            head[b_num] = tail[b_num] = 0
            break

    print(b_num + 1)


# 입력:
q = int(input())
for _ in range(q):
    elems = list(map(int, input().split()))
    q_type = elems[0]

    if q_type == 100:
        build_factory(elems)
    elif q_type == 200:
        drop_off(elems)
    elif q_type == 300:
        remove(elems)
    elif q_type == 400:
        find(elems)
    else:
        broken_belt(elems)

# from collections import defaultdict

# max_m = 10

# n,m,q = -1,-1,-1

# weight = {}

# # d_linked
# prv,nxt = defaultdict(lambda: 0),defaultdict(lambda: 0)

# # 각 벨트별로 head, tail id
# head = [0]*max_m
# tail = [0]*max_m

# # 벨트 망가졌는지 확인
# broken = [0]*max_m

# # 물건별로 벨트 번호
# # 벨트 번호가 -1이면 사라진것
# belt_num = defaultdict(lambda: -1)

# def build_factory(elems):
#     global n,m

#     n,m = elems[1],elems[2]
#     ids,ws = elems[3:3+n], elems[3+n:3+n+n]

#     for i in range(n):
#         # id : weight
#         weight[ids[i]] = ws[i]

#     size = n//m
#     for i in range(m):
#         # [id, , , ,]
#         head[i] = ids[i*size]
#         tail[i] = ids[(i+1)*size-1] # 다음 head전 => tail

#         for j in range(i*size,(i+1)*size):
#             # id : 벨트 번호
#             belt_num[ids[j]] = i

#             # nxt,prv
#             if j<(i+1) * size-1: # tail보다 작으면
#                 # 다음것 =>j+1
#                 nxt[ids[j]] = ids[j+1]

#                 # 이전 것=>j
#                 prv[ids[j + 1]] = ids[j]

# def remove_id(_id, remove_belt):
#     b_num = belt_num[_id]

#     # 벨트 번호 제거
#     if remove_belt:
#         belt_num[_id] = -1

#     # 하나 남았으면 => 다 지운다.
#     if head[b_num]==tail[b_num]:
#         head[b_num]=tail[b_num]=0

#     # 삭제가 head라면
#     elif _id == head[b_num]:
#         nid = nxt[_id]
#         head[b_num] = nid # head바뀌고
#         prv[nid]=0

#     # 삭제가 tail이면
#     elif _id == tail[b_num]:
#         pid = prv[_id]
#         tail[b_num] = pid
#         nxt[pid] = 0

# def push_id(target_id, _id):
#     nxt[target_id] = _id
#     prv[_id] = target_id

#     b_num = belt_num[target_id]
#     if tail[b_num]==target_id: #target_id가 tail이었다면
#         tail[b_num]=_id

    
# def drop_off(elems):

#     w_max = elems[1]
#     w_sum = 0
#     for i in range(m):

#         # 부서짐
#         if broken[i]:
#             continue
    
#         # belt가 존재한다면 
#         if head[i]!=0:
#             _id = head[i]
#             w = weight[_id]

#             if w<=w_max:
#                 w_sum+=w

#                 remove_id(_id,True)

#             # 그렇지 않으면?
#             elif nxt[_id]!= 0: # tail이 아니라면
#                 remove_id(_id, False)
#                 push_id(tail[i],_id)

#     print(w_sum)

# def remove(elems):
#     r_id = elems[1]
#     if belt_num[r_id] == -1:
#         print(-1)
#         return
    
#     remove_id(r_id,True)
#     print(r_id)

# def find(elems):
#     f_id = elems[1]

#     # 이미 삭제
#     if belt_num[f_id] == -1:
#         print(-1)
#         return
    
#     # 현재 어느 벨트에 있는지 확인
#     b_num = belt_num[f_id]
#     if head[b_num] != f_id: # head가 아니라면
#         orig_tail = tail[b_num]
#         orig_head = head[b_num]

#         now_tail = prv[f_id]
#         tail[b_num] = now_tail
#         nxt[now_tail] = 0

#         nxt[orig_tail] = orig_head
#         prv[orig_head] = orig_tail

#         head[b_num] = f_id
    
#     print(b_num+1)

# def broken_belt(elems):

#     b_num = elems[1]
#     b_num-=1 # idx 0부터 시작이기 때문

#     if broken[b_num]:
#         print(-1)
#         return
    
#     broken[b_num] = 1

#     # 빈 벨트
#     if head[b_num]==0:
#         print(b_num+1)
#         return
    
#     nxt_num = b_num
#     while True:
#         nxt_num = (nxt_num+1)%m

#         if not broken[nxt_num]:

#             # 빈 벨트
#             if tail[nxt_num] == 0:
#                 head[nxt_num] = head[b_num]
#                 tail[nxt_num] = tail[b_num]
#             else:
#                 push_id(tail[nxt_num],head[b_num])
#                 tail[nxt_num] = tail[b_num]
        
#         # head부터 tail까지 belt_num갱시
#         _id = head[b_num]
#         while _id!=0:
#             belt_num[_id] = nxt_num
#             _id = nxt[_id]
        
#         head[b_num] = tail[b_num] = 0 # 고장
#         break
#     print(b_num+1)


# # 입력:
# q = int(input())
# for _ in range(q):
#     elems = list(map(int, input().split()))
#     q_type = elems[0]

#     if q_type == 100:
#         build_factory(elems)
#     elif q_type == 200:
#         print(head)
#         drop_off(elems)
        
#     elif q_type == 300:
#         print(head)
#         remove(elems)
#     elif q_type == 400:
#         print(head)
#         find(elems)
#     else:
#         print(head)
#         broken_belt(elems)




# class Node:
#     def __init__(self,key=None):
#         self.key = key
#         self.prev = None
#         self.next = None
        

# class d_linked_lst:

#     def __init__(self):
#         self.head = self
#         self.tail = self
#         self.size = 0

#     def findSize(self):
#         return self.size

#     def addFront(self,key):
#         if self.size==0:
#             self.head = Node(key)
#             self.tail = self.head
#             self.size+=1

#         else:
#             # node <-> head
#             node = Node(key)
#             self.head.prev = node
#             node.next = self.head
#             self.head = node
#             self.size+=1

#     def addBack(self,key):
#         if self.size==0:
#             self.head = Node(key)
#             self.tail = self.head
#             self.size+=1
#         else:
#             # tail <-> node
#             node = Node(key)
#             self.tail.next = node
#             node.prev = self.tail
#             self.tail = node
#             self.size+=1

#     def checkFront(self):
#         return self.head.key

#     def popFront(self):
#         if self.size ==0:
#             return None
#         node = self.head
#         self.head = node.next
#         # self.head.prev = None
#         self.size-=1
#         return node.key
    
#     def popBack(self):
#         if self.size==0:
#             return None
#         node = self.tail
#         self.tail = node.prev
#         # self.tail.next = None
#         self.size-=1
#         return node.key

#     def remove(self,id):
#         if self.size==0:
#             return None
        
#         if self.head.key[0]==id:
#             ans_id,_ = self.popFront()
#             return ans_id
        
#         elif self.tail.key[0]==id:
#             ans_id,_ = self.popBack()
#             return ans_id
        
#         else:
#             node = self.head
#             for _ in range(self.size):
#                 if node.key[0]==id:
#                     # prev  id_node  next
#                     prev_node = node.prev
#                     next_node = node.next

#                     prev_node.next = next_node
#                     next_node.prev = prev_node
                    
#                     # node.next = None
#                     # node.prev = None
#                     self.size-=1
#                     return node.key[0]
#                 node = node.next
    
#     def checkBox(self,id):
#         if self.size==0:
#             return None

#         if self.head.key[0]==id:
#             return self.head.key[0]
        
#         else:
#             node = self.head
#             for _ in range(self.size):
#                 if node.key[0]==id:
#                     # node~tail head prev_node
#                     self.tail.next = self.head
#                     self.head.prev = self.tail
                    
#                     prev_node = node.prev
#                     # prev_node.next = None

#                     self.tail = prev_node
#                     self.head = node
#                     # self.head.prev = None
                    
#                     return  node.key[0]
#                 node = node.next

#     def together(self,dlst):

#         self.tail.next = dlst.head
#         dlst.head.prev = self.tail
#         self.tail = dlst.tail
#         self.size+= dlst.findSize()


#     def check(self):

#         lst = []
#         node = self.head
#         for _ in range(self.size):
#             lst.append(node.key)
#             node = node.next
#         return lst


# q = int(input())
# for _ in range(q):
    
#     order,*tmp = map(int,input().split())
    
#     if order==100:
#         n,m,*ids_weights = tmp
#         ids = ids_weights[:len(ids_weights)//2]
#         weights = ids_weights[len(ids_weights)//2:]
#         belts = {}
#         belts_set = {}
#         broken = [0]*m

#         b_n = 0
#         for i in range(0,n,n//m):
#             # 생성
#             dlst = d_linked_lst()
#             belts[b_n] = dlst
#             belts_set[b_n] = set()
#             for j in range(i,i+n//m):
#                 # add
#                 belts[b_n].addBack((ids[j],weights[j]))
#                 belts_set[b_n].add(ids[j])                
#             b_n+=1
    
#     elif order==200:
#         mx = tmp[0]
#         total = 0
#         for i2 in range(m):
#             if belts[i2].findSize()==0 or broken[i2]:
#                 continue 
            
#             else:
#                 if belts[i2].checkFront()[1]<=mx:
#                     i2_id,i2_w = belts[i2].popFront()
#                     belts_set[i2].remove(i2_id)
#                     total+=i2_w
#                 else:
#                     i2_id,i2_w = belts[i2].popFront()
#                     belts[i2].addBack((i2_id,i2_w))

#         # print('order 200 : ', total)
#         print(total)

    
#     elif order==300:
#         r_id = tmp[0]
#         for i3 in range(m):
#             if r_id in belts_set[i3]:
#                 belts_set[i3].remove(r_id)
#                 # print('order 300 :', belts[i3].remove(r_id))
#                 print(belts[i3].remove(r_id))
#                 # print(belts[i3].check())
#                 break
#         else:
#             # print('order 300 :', -1)
#             print(-1)


#     elif order==400:
#         f_id = tmp[0]
#         for i4 in range(m):
#             if f_id in belts_set[i4]:
#                 belts[i4].checkBox(f_id)
#                 # print('order 400 :', i4+1)
#                 print(i4+1)
#                 break
#         else:
#             print(-1)
#             # print('order 400 :', -1)


#     elif order==500:
#         b_num = tmp[0]


#         if belts[b_num-1].findSize()==0 or broken[b_num-1]:
#             print(-1)

#         else:
#             for i5 in range(m-1):
#                 if (belts[(i5+b_num)%m].findSize()==0) or broken[(i5+b_num)%m]:
#                     continue

#                 else:
#                     belts[(i5+b_num)%m].together(belts[b_num-1])
#                     broken[b_num-1]=1
#                     belts_set[(i5+b_num)%m]=belts_set[(i5+b_num)%m] | belts_set[b_num-1]
#                     belts_set[b_num-1] = set()
#                     print(b_num)
#                     break

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