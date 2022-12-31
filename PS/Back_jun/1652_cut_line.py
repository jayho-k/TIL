'''
4 11
802
743
457
539

'''
def caculate(mid):
    total = 0
    for l in lst:
        total += l//mid
    return total

k,n = map(int,input().split())
total = 0
lst = []
for _ in range(k):
    t = int(input())
    total += t
    lst.append(t)

start = 1
end = total//n
mx = 0

while start<=end:

    mid = (start+end)//2
    key = caculate(mid) 
    if key==n:
        start = mid+1

    elif key>n:
        start = mid+1
    
    else:
        end = mid-1

print(end)