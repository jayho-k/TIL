'''

1
2
0 0 1 0 0 1 0 0
1 0 0 1 1 1 0 1
0 0 1 0 1 1 0 0
0 0 1 0 1 1 0 1
1 1
3 -1
'''
from collections import deque

def left(cg, rotate):
    
    for lg in range(cg-1,0,-1):
        if gears[lg][2]==gears[lg+1][-2]:
            break
        else:
            rotate*=-1
            change[lg]= rotate

def right(cg, rotate):

    for rg in range(cg+1,5):
        if gears[rg][-2]==gears[rg-1][2]:
            break
        else:
            rotate*=-1
            change[rg]= rotate
    

for tc in range(1,int(input())+1):
    k = int(input())
    gears = {}
    for gi in range(1,5):
        gears[gi] = deque(list(map(int,input().split())))
    
    for _ in range(k):
        cg, rotate = map(int,input().split())
        change = [0]*5
        change[cg]=rotate
        left(cg,rotate)
        right(cg,rotate)
        for ch in range(1,len(change)):
            gears[ch].rotate(change[ch])
    ans = 0
    for g in range(1,5):
        if gears[g][0]:
            ans+=(2**(g-1))
    print(f"#{tc} {ans}")