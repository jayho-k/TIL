


'''
60
100

10,000이하
'''
n = int(input())
m = int(input())

tmp = [0,0]+ [1]*10001

prime = []
for i in range(2,10001):

    for j in range(i*2, 10001, i):
        if tmp[j]:
            tmp[j] = 0

total = 0
mn = 1e9
for a in range(n,m+1):
    if tmp[a] == 1:
        total += a

        if mn > a:
            mn = a

if total == 0:
    print(-1)

else:
    print(total)
    print(mn)



