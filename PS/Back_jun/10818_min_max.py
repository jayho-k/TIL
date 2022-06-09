'''
5
20 10 35 30 7
'''

n = int(input())
lst = list(map(int,input().split()))

mn = 1e9
mx = -1e9

for i in lst:
    
    if mn > i:
        mn = i

    if mx < i:
        mx = i

print(mn, mx)