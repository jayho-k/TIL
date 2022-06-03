'''
5 3
1
2
8
4
9

ans = 3
'''

n,c = map(int,input().split())

lst = [int(input()) for _ in range(n)]
lst.sort()


strt = 1
end = lst[-1] - lst[0]
ans = 0

while strt<=end:

    mid = (strt+end)//2
    now = lst[0]
    cnt = 1 # 첫번째
    
    # install router
    for i in range(1,len(lst)):
        if lst[i]>=now+mid:
            cnt+=1
            now = lst[i]

    # 공유기 보다 많을 경우 => 넓혀야함
    if cnt >= c:
        strt = mid+1
        ans = mid

    # 줄여야함
    else:
        end = mid-1


print(ans)