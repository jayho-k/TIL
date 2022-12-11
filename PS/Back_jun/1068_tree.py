'''

9
-1 0 0 2 2 4 4 6 6
4

6
1 2 3 4 -1 4
5

2
-1 0
1 
(루트노드 단 하나만 남음)
'''

def dfs(st):
    global cnt,remv
    if tree[st] == []:
        cnt += 1
        return
        
    for t in tree[st]:
        dfs(t)

n = int(input())
parent = list(map(int,input().split()))
match = list(range(n))
tree = [[] for _ in range(51)]
remv = int(input())
cnt = 0
root = -1
for i in range(len(parent)):
    if parent[i] == -1:
        root = i
    else:
        tree[parent[i]].append(i)

re_parent = tree[parent[remv]]
tree[remv] = []
if root == remv:
    print(0)
else:
    dfs(root)

    # 부모노드의 오직 지우려는 자식노드밖에 없다면=> 일직선 => 그때는 
    if len(re_parent)==1 and re_parent[0]==remv:
        print(cnt)
    else:
        print(cnt-1)