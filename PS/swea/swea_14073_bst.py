'''
1. 문제
3
6
8
15

2. 문제
level 순으로 lst 가 주어졌을 경우
후위순회를 시켜 답을 구하는 방법

'''

level = [5,7,6,4,3,2,5,10,15,11,20,30]
tree = []
# 중위순회로 만들어야함

def inorder(root):
    global cnt
    if root<=len(level):
        inorder(root*2)
        tree.append(level[root-1])
        inorder(root*2+1)
cnt = 1
inorder(1)
print(tree)


# def inorder(root):
#     global cnt
#     if root<n:
#         inorder(root*2)
#         tree.append(root)
#         inorder((root*2)+1)


# for _ in range(int(input())):
#     n = int(input())
#     # tree = [0]*(n+1)
#     tree = []
#     cnt = 1
#     inorder(1)
#     print(tree)
