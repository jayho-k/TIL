'''
12 1
1 2 1
2 3 2
3 4 3
4 5 1
5 6 2
6 7 1
5 8 1
4 9 2
4 10 3
10 11 1
10 12 3

'''

def findGiga(node):

    global giga_node, pillar
    if len(tree[node])>2 or (len(tree[node])==1 and node != root):
        giga_node = node
        return

    visited[node]=1
    for tnode in tree[node]:
        if visited[tnode[0]]==0:
            pillar += tnode[1]
            findGiga(tnode[0])


def findLongest(node,length):

    global longest
    if len(tree[node]) == 1:
        longest = max(length,longest)
        return

    for t,d in tree[node]:
        if visited[t]==0:
            visited[t]=1
            findLongest(t,length+d)

import sys
sys.setrecursionlimit(10**6)
input = sys.stdin.readline
n, root = map(int,input().split())
tree = [[] for _ in range(200002)]
for _ in range(n-1):
    a,b,d = map(int,input().split())
    tree[a].append((b,d))
    tree[b].append((a,d))

giga_node = -1
pillar = 0
longest = 0
visited = [0]*200002
findGiga(root)
if giga_node == -1:
    giga_node = root
# print(visited)
visited[giga_node]=1
findLongest(giga_node,0)
print(pillar,longest)
# print(visited)
# visited를 다시 만들어 주었다 => 그럴 필요가 없음
# 시간 초과가 뜨게 된다