'''


5 3 2
4 1
5 2
3 3
'''

# T = int(input())
T = int(input())
for tc in range(1,T+1):

    # 노드, 리프노드, 노드번호
    n,l,node_num = map(int, input().split())
    tree = [0]*(n+2)

    for i in range(l):
        l_num, num = map(int,input().split())
        tree[l_num] = num

    for i in range(n,0,-1):
        if tree[i] == 0:
            tree[i] = tree[i*2]+tree[i*2+1]
    
    print(f'#{tc} {tree[node_num]}')