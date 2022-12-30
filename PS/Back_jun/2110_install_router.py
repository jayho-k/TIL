'''
5 3
1
2
8
4
9

'''

def caculate(mid):
    cnt = 1
    now = lst[0]
    for i in range(1,len(lst)):
        if lst[i]>=mid+now:
            cnt+=1
            now = lst[i]
    return cnt


n,c = map(int,input().split())
lst = [int(input()) for _ in range(n)]
lst.sort()

# 초기화
start = 1
end = lst[-1]-lst[0]
while start<=end:

    mid = (start+end)//2
    cnt = caculate(mid)
    if cnt == c:
        start = mid+1

    elif cnt>c:
        start = mid+1

    else:
        end = mid-1

print(end)

