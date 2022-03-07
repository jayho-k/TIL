'''
1. 노드 생성(key,parant,left.right)
2. bst생성
    init
    find_loc
    search
    insert
    delete

'''
# Node
class Node:
    def __init__(self,key=None,parent=None,left=None,right=None):
        self.key = key
        self.parent = parent
        self.left = left
        self.right = right

    def __str__(self):
        return str(self.key)

# Binary Search Tree
class BST:

    def __init__(self): 
        #root, size, height
        self.root = None
        self.size = 0
        self.height = 0

    def preorder(self,v):
        if v != None:
            print(self.key)
            self.preorder(v.right)
            self.preorder(v.left)

    
    def find_loc(self,key):
        if self.size == 0:
            return None

        p = None
        v = self.root
        while v != None:
            if v.key == key:
                # 키값 찾음 반환
                return v

            elif v.key < key:
                # 찾고 싶은게 더 커? 오른쪽으로 가면 있음
                p = v
                v = v.right
            
            else:
                # 찾고 싶은게 더 작아? 왼쪽으로 가면 있음
                p = v
                v = v.left
        return p

    def search(self, key):

        v = self.find_loc(key)
        # 만약에 key값이 없으면 None을 반환함
        # 그래서 p.key == key라는 소리가 Tree내에 값이 존재하면? 이라는 뜻
        if v == None:
            return None
        else:
            return v

        # if p and p.key == key:
        #     return p

        # else:
        #     return None

    def insert(self, key):
        p = self.find_loc(key)
        if p == None or p.key != key:
            # p가 root노드일때랑 아닐때
            v = Node(key)
            print(p)
            if p == None:
                self.root = v
            
            else:
                # parent 정의, 넣는 위치 정해줘야함
                v.parent = p
                if v.key >= key:
                    # 내가 집어넣으려고하는게 더 작아? 그럼 왼쪽으로
                    p.left = v
                else:
                     # 내가 집어넣으려고하는게 더 커? 그럼 오른쪽으로
                    p.right = v
            self.size += 1
            return v

        else:
            print('존재')
            return None
            
    def delete(self):
        pass

b = BST()

for i in range(1,11):
    b.insert(i)

print(b.size)
print(b.find_loc(3))