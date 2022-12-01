'''
6
1 2 3 4 1 6
7 8 9 1 4 2
2 3 4 1 1 3
6 6 6 6 9 4
9 1 9 1 9 5
1 1 1 1 9 9

(x+d1, y-d1)
(x+d2, y+d2)
(x+d1+d2, y-d1+d2)
(x+d2+d1, y+d2-d1)
'''
import sys
from pprint import pprint
from itertools import permutations
input = sys.stdin.readline
n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
visited = [[0] for _ in range(n)]
d_lst =  list(permutations(list(range(1,n+1)),2))
tmp = []
ans = 1e9

def caculate(x,y,d1,d2):

    global total,ans
    first,second,third,fourth = 0,0,0,0
    
    # 1
    y1 = y+1
    for f in range(x+d1):
        if f >= x:
            y1-=1
        first += sum(grid[f][:y1])

    # 2
    y2 = y+1
    for s in range(x+d2+1):
        if s > x:
            y2+=1
        second += sum(grid[s][y2:])

    # 3
    y3 = y-d1
    for t in range(x+d1,n):
        third += sum(grid[t][:y3])
        if t < x+d1+d2:
            y3 += 1

    # 4
    y4 = y+d2
    for fr in range(x+d2+1,n):
        fourth += sum(grid[fr][y4:])
        if fr <= x+d2+d1:
            y4-=1

    # 5
    fifth = total-first-second-third-fourth

    # answer
    mx = max(first,second,third,fourth,fifth)
    mn = min(first,second,third,fourth,fifth)
    if ans >= mx-mn:
        # print('x :',x,'y :',y)
        # print('d1 :',d1,'d2 :',d2)
        # print('first :',first)
        # print('second :',second)
        # print('third :',third)
        # print('fourth :',fourth)
        # print('total :',total)
        # print('*'*30)
        ans = mx-mn
        # ans = min(ans, mx-mn)

total = 0
for ty in range(n):
    total += sum(grid[ty])


for x in range(n):
    for y in range(1,n):
        for d1 in range(1,n+1):
            for d2 in range(1,n+1):        
                if 0<=x+d1-1<n and 0<=x+d2-1<n and\
                    0<=x+d2+d1<n and 0<=y-d1<n and 0<=y+d2<n and\
                    0<=y-d1+d2-1<n:
                    caculate(x,y,d1,d2)

print(ans)

