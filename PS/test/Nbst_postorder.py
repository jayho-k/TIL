'''
이진트리
lst(level)가 주어졌을때 => 후위순회로 바꾸기

lst = 5,7,6,4,3,2,5,10,15,11,20,30

ans = [10, 15, 4, 11, 20, 3, 7, 30, 2, 5, 6, 5]

'''
tree = []
def postorder(root):

    if root<=len(lst):
        postorder(root*2)
        postorder(root*2+1)
        tree.append(lst[root-1])

lst = [5,7,6,4,3,2,5,10,15,11,20,30]
postorder(1)
print(tree)

