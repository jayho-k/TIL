from turtle import left


class Node:
    def __init__(self, key):
        self.key = key
        self.parent = self.left = self.right = None
        # 부모, 왼쪽, 오른쪽을 None으로 초기화 시킨다.

    def __str__(self):
        return str(self.key)

# 이부분은 BST와 동일하다
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

    def rotateRight(self, z):
        if z == None:
            return
        x = z.left
        if x == None:
            return
        b = x.right # 이부분을 조금더 이해할 필요가 있음  # 1
        #2
        x.parent = z.parent
        if z.parent != None:
            if z.parent.left == z:
                z.parent.left = x
            else:
                z.parent.right = x
        #3
        x.right = z
        #4
        z.parent = x
        z.left = b
        if b != None:
            b.parent = z

        if self.root == z:
            self.root = x

class AVL(BST):
    # 상속을 받아온다
    # 노드에는 각각의 left right parant등등이 있었다
    # 하지만 AVL트리에서는 hieght라는 정보가 필요하다
    # 왜냐하면 정의자체가 왼쪽 부트리와 오른쪽 부트리의 h의 차가 1이하인 트리이기 떄문
    # 즉 서로의 높이차가 1이하인지 따져줘야한다.

    # insert, delete등등은 높이가 달라지게 된다
    # 따라서 height의 정보가 업데이트를 해줘야한다. 

    def insert(self, key):
        '''
        순서:
        # xyz가 일자인 경우 ==> 그림 1과같이 진행 ==> rotation1회로 가능
        # xyz가 지그재그인 경우 ==> 그림 2와같이 진행 ==> rotation 2회를 해주어야 한다.
        # 두가지 경우를 따져줘야한다

        1. v = super(AVL,self).insert(key)
        2. find xyz 
            (위에서부터 z는 처음으로 AVL조겅이 꺠진 노드)
            (y는 z의 자식노드)
            (x는 y의 자식노드 사진 참조)
        3. w = rebalence (x,y,z)
        4. if w.parent == None:
            self.root = w
        '''
        # 1
        v = super(AVL,self).insert(key) # 현재 클래스의 이름과 객체를 말해주면 된다.

        # 2. 
        # rebalance를 해주어한다.
        # z를 찾아줘야한다 (균형이 맞지 않는 부모노드)
        # z가 존재할때와 아닐때를 나눠줘야한다

    def delete(self, u):
        v = super(AVL, self).deleteByMerging(u)
        # v는 u라는 노드를 지워서 균형이 깨질수 있는 가장 깊은 노드를 반환해주게 된다
        # 즉 그림에서는 p가 된다
        # 따라서 return해줘야하는 값이 parent라고 delete함수에서 정의해준것이다.
        while v != None:
            if v is not balanced: # 수도 코드임
                z = v
                if z.left.height >= z.tight.height:
                    y = z.left
                else:
                    y = z.right

                if y.left.height >= y.right.height:
                    x = y.left

                else:
                    x = y.right
            v = rebalence(x,y,z)

            w = v
            v = v.parent
        # while문에서 빠져나왔을 떄는 v == None상태가 된다
        # v가 None이라는 뜻은 root노드의 부모가 되었다는 뜻이고
        # w가 root가 되었다는 뜻이다
        # 즉 끝까지 올라갔다는 뜻이 된다.
        # rotation은 돌리지 않더라도 부모노드에서 균형이 맞는지 아닌지를
        # 계속해서 봐줘야하기 때문에 그렇게 되는 것이다.
        # w == root가 된다
        self.root = w
