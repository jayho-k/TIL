'''

1
5 2
1 3
2 4



'''

for tc in range(1,int(input())+1):
    N,Q = map(int,input().split())
    lst = [0]*(N)
    for i in range(1,Q+1):
        l,r = map(int,input().split())
        for j in range(l,r+1):
            lst[j-1]=i
    print(f'#{tc}',*lst)
