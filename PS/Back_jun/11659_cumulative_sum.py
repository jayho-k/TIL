'''
5 3
5 4 3 2 1
1 3
2 4
5 5

'''
import sys
input = sys.stdin.readline

n,m = map(int,input().split())
lst = list(map(int,input().split()))
tmp = [0]*(n+1)
store = [0]*m

tmp[1] = lst[0]
for i in range(1,n):
    tmp[i+1] = lst[i]+tmp[i]

for _ in range(m):
    s,e = map(int,input().split())
    st = tmp[s-1]
    end = tmp[e]
    print(end-st)