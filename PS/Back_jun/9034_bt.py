'''

inorder
노드의 깊이를 알아내는 문제

'''
def make_tree(value,d):

    if d == level:
        return
    v = len(value)//2
    tree[d].append(value[v])

    make_tree(value[:v],d+1)
    make_tree(value[v+1:],d+1)




level = int(input())
value = list(map(int,input().split()))
tree = [[] for _ in range(level)]
order = list(range(1,2**level))
make_tree(value,0)
for t in tree:
    print(*t)
