'''
단절점(cut vertex) : 
해당 정점을 제거하였을 때, 
그 정점이 포함된 그래프가 2개 이상으로 나뉘는 경우, 
이 정점을 단절점이라 한다.
==> 자식노드의 자식이 2개 이상

단절선(bridge) : 
해당 간선을 제거하였을 때, 
그 간선이 포함된 그래프가 2개 이상으로 나뉘는 경우, 
이 간선을 단절선이라 한다.
==> 자식노드의 자식노드의 자식이 2개이상

5
1 2
2 3
3 4
4 5
4
1 1
1 2
2 1
2 2
'''
def findVertex(q2):

    if len(tree[q2]) > 1:
        return 'yes'
    else:
        return 'no'

n = int(input())
tree = [[] for _ in range(n+1)]
visited = [0]*(n+1)
for _ in range(n-1):
    s,f = map(int,input().split())
    tree[s].append(f)
    tree[f].append(s)

q = int(input())
question = [list(map(int,input().split())) for _ in range(q)]
for q1,q2 in question:
    if q1 == 1:
        print(findVertex(q2))
    else:
        print('yes')




