'''
1+1+1+1
1+1+2
1+2+1
2+1+1
2+2
1+3
3+1
'''

# dp





# dfs
def dfs(d):
    global cnt

    if d == n:
        cnt += 1
        return

    elif d > n:
        return

    else:
        dfs(d+1)
        dfs(d+2)
        dfs(d+3)

T = int(input())
for tc in range(1,T+1):

    n = int(input())
    cnt = 0
    dfs(0)

    print(cnt)

