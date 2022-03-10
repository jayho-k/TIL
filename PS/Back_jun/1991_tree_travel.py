'''
tree 순회
7
A B C
B D .
C E F
E . .
F . G
D . .
G . .
'''

import string

a_lst = list(string.ascii_uppercase)

tree = {}

n = int(input())
for i in range(n):
    root, r, l = input().split()
    tree[root] = [r,l]

pre_lst = []
def pre(node):
    pre_lst.append(node)
    if tree[node][0] != '.': pre(tree[node][0])
    if tree[node][1] != '.': pre(tree[node][1])

in_lst = []
def ino(node):
    if tree[node][0] != '.': ino(tree[node][0])
    in_lst.append(node)
    if tree[node][1] != '.': ino(tree[node][1])

pst_lst = []
def pst(node):
    if tree[node][0] != '.': pst(tree[node][0])
    if tree[node][1] != '.': pst(tree[node][1])
    pst_lst.append(node)

pre('A')
ino('A')
pst('A')

print(''.join(pre_lst))
print(''.join(in_lst))
print(''.join(pst_lst))


 
