'''

'''

n = int(input())
m = int(input())

lst = [0]*(n+1)
for _ in range(m):
    s,f = map(int,input().split())
    for i in range(s,f):
        lst[i] =1

print(lst.count(0)-1)