'''
4
1 3 5 7

'''

t = int(input())
lst = list(map(int,input().split()))

tmp = [0,0]+[1]*1001

# primes = []
m = int(1001**0.5)
for i in range(2,1001):
    if tmp[i] == 1:
        # primes.append(i)

        for j in range(2*i,1001,i):
            tmp[j] = 0

cnt = 0
for a in lst:
    if tmp[a] == 1:
        cnt += 1

print(cnt)
