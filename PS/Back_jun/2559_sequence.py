'''
10 2
3 -2 -4 -9 0 3 7 13 8 -3
'''
import sys
n, m = map(int, sys.stdin.readline().split())
lst = list(map(int,sys.stdin.readline().split()))

lst2 = [sum(lst[:m])]
for i in range(n-m):
    sm = lst2[i]-lst[i]+lst[i+m]
    lst2.append(sm)

print(max(lst2))