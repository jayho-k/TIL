'''
10
10 -4 3 1 5 6 -35 12 21 -1

'''
from itertools import accumulate
n = int(input())
lst = list(accumulate(map(int,input().split())))
mx = lst[0]
j = 0
for i in range(1,n):
    mx = max(lst[i], lst[i]-lst[j],mx)
    if lst[i]<lst[j]:
        j=i
print(mx)
