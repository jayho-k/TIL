'''

2

1
4
-1000 0 3 5
1000 0 2 3
0 1000 1 7
0 -1000 0 9


1
4
-3 0 3 5
3 0 2 3
0 3 1 7
0 -3 0 9

1
4
-4 0 3 5
4 0 2 3
0 4 1 7
0 4 0 9

1
4
-1 1 3 3
0 1 1 1
0 0 2 2
-1 0 0 9

'''
from pprint import pprint
from collections import defaultdict
def find_total(atom):
    total = 0
    while 1:
        new_atom = defaultdict(list)
        for y,x,d,k in atom:
            ny = y+dy[d]
            nx = x+dx[d]
            if -2000<=ny<=2000 and -2000<=nx<=2000:
                new_atom[(ny,nx)].append((d,k))

        atom = []
        for na in new_atom:
            if len(new_atom[na])>=2:
                for _,ak in new_atom[na]:
                    total+=ak    
            else:
                atom.append((na[0],na[1],new_atom[na][0][0],new_atom[na][0][1]))

        if len(atom)<=1:
            return total

for tc in range(1,int(input())+1):
    n = int(input())

    dy = [1,-1,0,0]
    dx = [0,0,-1,1]
    atom = []
    for _ in range(n):
        x,y,d,k = map(int,input().split())
        atom.append((2*y,2*x,d,k))
    total = find_total(atom)


    print(f"#{tc} {total}")
