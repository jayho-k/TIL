'''

4 6
0 1 10
0 2 7
1 4 2
2 3 10
2 4 3
3 4 10

'''

def find_p(p,x):
    # 자기 자신이 아니라면
    if p[x] != x:
        # 부모노드 찾기
        p[x] = find_p(p,p[x])
    return p[x]

def union(p,a,b):    
    # a = find_p(p,a)
    # b = find_p(p,b)
    if a<b:
        p[b] = a
    else:
        p[a] = b

T = int(input())
for tc in range(1,T+1):
    n,m = map(int,input().split())
    lsts = []
    p = [0]*(n+1)

    for i in range(len(p)):
        p[i] = i

    for _ in range(m):
        a,b,c = map(int,input().split())
        lsts.append((c,a,b))
        lsts.append((c,b,a))

    lsts.sort()

    total = 0
    for lst in lsts:
        c,a,b = lst
        p_a = find_p(p,a)
        p_b = find_p(p,b)

        # 사이클 발생여부
        if p_a != p_b:
            union(p,p_a,p_b)
            total += c

    print(f'#{tc} {total}')

