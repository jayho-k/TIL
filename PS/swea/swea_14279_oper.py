'''
dfs

1. 4개 연산
    +1, -1, *2, -10 
2. 계산 후 n이 m을 넘을 때
    return
3. 계산 도중 1e9넘으면 
    return
4. d가 적은것을 선택
    d가 30 넘으면 return

1
2 7

3
2 7
3 15
36 1007
'''
def dfs(d,v):
    global mn

    if v > m:
        print(v)
        return

    if v == m:
        mn = min(mn, d)
        return

    if d >10:
        return

    dfs(d+1, v*2)
    dfs(d+1, v+1)


T = int(input())
for tc in range(1,T+1):

    n, m = map(int,input().split())
    mn = 1e9

    dfs(0,n)

    print(mn)