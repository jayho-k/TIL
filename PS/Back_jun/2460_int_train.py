'''
0 32
3 13
28 25
17 5
21 20
11 0
12 12
4 2
0 8
21 0
'''
total = 0
mx = 0
for i in range(10):
    out, inn = map(int,input().split())
    total -= out
    if mx < total:
        mx = total
    
    total += inn
    if mx < total:
        mx = total

print(mx)
    