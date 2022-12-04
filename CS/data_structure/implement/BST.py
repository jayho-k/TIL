'''
BST 정리
- insert
- search
- delete
- pre_order
- in_order
- post_order

'''

# 1. create node
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# 2. BST
class BST:
    def __init__(self,root=None):
        self.root = root
        self.size = 0
        self.depth = 0

    
    def insert(self,val):
        # find parent node // do not confused with root
        self.root = self._insert(self.root,val)
        return self.root is not None

    def _insert(self,node,val):
        # node.val : current  /  val : target
        # if the end of node => create Node
        if node is None:
            return TreeNode(val)
        
        if val < node.val: # smaller : left => compare with next left node
            node.left = self._insert(node.left, val)
        
        else: # bigger : right
            node.right = self._insert(node.right, val)

        return node

    # why use? : to check if what I find is existed
    def search(self,val):
        return self._search(self.root, val) 

    def _search(self,node,val):

        if node is None or node.val==val:
            return node
            
        if val < node.val:
            return self._search(node.left,val)

        else:
            return self._search(node.right,val)

    def delete(self,val):
        self.root = self._delete(self.root, val)

    def _delete(self,node,val):
        
        if node is None:
            return None

        if  val < node.val:
            node.left = self._delete(node.left, val)

        elif val > node.val:
            node.right = self._delete(node.right, val)

        else: # if find what I want to delete
            if node.left is None:
                # node.right will move to the space that node was ()
                return node.right

            elif node.right is None:
                return node.left

            # if 둘다 존재할 경우 => 최솟값을 찾아야 한다.
            node.val = BST._get_min_val(node.right)
            node.right = self._delete(node.right, node.val)
        
        return node

    @classmethod
    def _get_min_val(cls,node):
        min_val = node.val
        while node.left:
            min_val = node.left.val
            node = node.left
        return min_val


    # preorder : left => current => right
    def _preorder(self, node):
        if node:
            print(node.val, end=" ")
            self._preorder(node.left)
            self._preorder(node.right)

    # inorder : left => current => right
    def _inorder(self, node):
        if node:
            self._inorder(node.left)
            print(node.val, end=" ")
            self._inorder(node.right)

    # postorder : left => right => current 
    def _postorder(self, node):
        if node:
            self._postorder(node.left)
            self._postorder(node.right)
            print(node.val, end=" ")

    def to_list(self):
        return self._to_list(self.root)
    
    def _to_list(self,node):
        if node is None:
            return []
        return self._to_list(node.left) + [node.val] + self._to_list(node.right)

    def print_by_ascending(self):
        self._inorder(self.root)

if __name__ == '__main__':
    nums = [10, 3, 4, 11, 32, 21, 45, 8, 1, 18]
    bst = BST()
    for n in nums:
        bst.insert(n)

    print('\n\n오름 차순 정렬 출력')
    bst.print_by_ascending()
    
    # Search
    assert bst.search(10) is not None
    assert bst.search(18) is not None
    assert bst.search(100) is None

    # Delete
    bst.delete(10)
    bst.delete(18)
    assert bst.search(10) is None
    # assert bst.search(18) is None

    print('\n\n오름 차순 정렬 출력')
    bst.print_by_ascending()

    print('\n\n이진 트리의 값을 오름 차순 정렬 리스트 자료구조로 반환')
    print(bst.to_list())    
