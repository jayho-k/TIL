class Node:
    def __init__(self, key):
        self.key = key
        self.parent = self.left = self.right = None
        # 부모, 왼쪽, 오른쪽을 None으로 초기화 시킨다.

    def __str__(self):
        return str(self.key)

# a = Node(6)
# b = Node(9)
# c = Node(1)
# d = Node(5)

# a.left = b
# a.right = c
# b.parent = c.parent = a
# b.right = d
# d.parent = b


# class Node:
#     def __init__(self, key):
#         self.key = key
#         self.parent = self.left = self.right = None
#         # 부모, 왼쪽, 오른쪽을 None으로 초기화 시킨다.

#     def preorder(self):  # 현재 방문중인 노드 = self  (MLR)
#         if self != None:
#             print(self.key)
#             if self.left:
#                 self.left.preorder()
            
#             if self.right:
#                 self.right.preorder()

#     def inorder(self):  # 현재 방문중인 노드 = self 
#         if self != None:
            
#             if self.left:
#                 self.left.inorder()
#             print(self.key)
#             if self.right:
#                 self.right.inorder()


#     def postorder(self):  # 현재 방문중인 노드 = self  
#         if self != None:
            
#             if self.left:
#                 self.left.postorder()
            
#             if self.right:
#                 self.right.postorder()

#             print(self.key)

#     def __str__(self):
#         return str(self.key)

# rootNode와 size를 저장해주게 된다


'''
insert가 해야할일
1. 처음일때는 => 그 값이 root노드가 되게 해주어야 한다.
2. 다음 4가 들어온다면 ==> 왼쪽에 붙도록 만들어야 함


'''


class BST:
    def __init__(self):
        self.root = None
        self.size = 0

    def __len__(self):
        return self.size

    def __iterator__(self):
        return self.root.__iterator__() 
        # 무슨 소리인지 확인// iterator, generator 부분을 공부해보기

    def find_loc(self, key): 
        # key값의 노드가 있다면 그 해당노드를 return 해준다
        # 없다면 그 노드가 삽입될 부모나드를 리턴한다

        # 비었다
        if self.size == 0:
            return None
        p = None #부모노드 ==> root의 부모노드는 없기때문에 None임
        v = self.root # 처음 값
        while v != None:
            if v.key == key:
                return v

            elif v.key < key:
                p = v
                v = v.right

            else:
                p = v
                v = v.left

        # while문을 빠져나왔다는 뜻은 찾지 못했다는 뜻 ==> 부모 노드 리턴
        return p


    # 이부분 이해하고 다시
    # def search(self, key):
    #     v = self.find_loc(key)
    #     if v == None:
    #         return None
    #     else:
    #         return v

    #insert
    # 계속해서 찾다가 None이 나오거나 작은 값이 나오면 거기를 들어가면 된다.
    # 1. p = find_loc(16)
    # 2. v = Node(16)
    # 3. update links
    # 4. size증가
    def insert(self, key):  # O(h) 시간이 든다
        p = self.find_loc(key)
        # 
        if p == None or p.key != key:
            # 여기서 p.key != key의 의미는 key값들이 중복이 되어 있지 않을 때라는 뜻

            v = Node(key)
            if p == None: 
                # 애초에 root Node라는 뜻이다
                # 왜냐하면 부모가 None인 노드는 root노드 밖에 없다

                self.root = v # root노드를 v로 바꿔줘

            else:  
                #p != , p.key != key
                # 뜻: p.key == key는 뜻은 중복이 되어 있다는 뜻다.
                # 왼쪽으로 가야할지 오른쪽으로 가야하는지 모른다
                v.parent = p
                if p.key >= key:
                    p.left = v
                else:
                    p.right = v

            self.size += 1

            return v
        else:
            print('key is already in tree')
            return None

    def deleteByMerging(self, x):
        a = x.left # 왼쪽 노드
        b = x.right # 오른쪽 노드
        p = x.parent # parents

        # c는 x자리를 대체할 노드
        # m = L 에서 가장큰 노드

        if a != None: #왼쪽 노드가 존재 할때

            c = a # 대체할 것임
            m = a # m은 a부터 시작

            while m.right:  # L에서 가장 큰 노드를 찾는 중
                m = m.right
                # --> m이 L에서 제일 큼 

            # m의 오른쪽 자식노드로 b를 연결한다

            if b != None: # R이 존재 할때
                b.parent = m

            m.right = b 
            # b가 None이어도 상관이 없는게
            # m right가 none이면 되기 때문

        else: # a == none일때
            c = b

        # parant와의 관계를 update해주어야 한다.
        if p != None:
            if c:
                c.parent = p

            if p.key < c.key:
                p.right = c

            else:
                p.left = c


        else: # p == None: ==> root ==> root를 지워달라는 뜻
            self.root = c
            if c:
                c.parent = None
            
        self.size -= -1


    def deleteByCopying(self):


        
        pass


# t = BST()
# print(t.root)