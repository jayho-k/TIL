"""
8
1 1 0 0 0 0 1 1
1 1 0 0 0 0 1 1
0 0 0 0 1 1 0 0
0 0 0 0 1 1 0 0
1 0 0 0 1 1 1 1
0 1 0 0 1 1 1 1
0 0 1 1 1 1 1 1
0 0 1 1 1 1 1 1



2
1 1
1 1


8
0 0 1 1 0 1 0 0
0 1 1 1 0 1 0 0
0 0 0 0 1 1 0 0
0 0 0 1 1 1 0 0
0 1 1 1 1 1 0 0
1 0 1 1 1 1 0 0
0 0 1 1 0 0 1 1
0 0 1 1 0 0 0 0

ans
18
13

"""
from pprint import pprint

def check(y,x,nn):
    z = 0
    o = 0
    store = set()
    for yy in range(y,y+nn):
        for xx in range(x,x+nn):
            store.add((yy,xx))
            if z and o:
                return False,0,0,set()

            if grid[yy][xx]==1:
                o+=1
            else:
                z+=1
    if z and o:
        return False,0,0,set()
    return True,z,o,store

def play():

    nn = n
    store = set()
    one,zero = 0,0
    while 1:
        for y in range(0,n,nn):
            for x in range(0,n,nn):
                
                if (y,x) not in store:

                    flag,z,o,store_tmp = check(y,x,nn)
                    store|=store_tmp
                    if flag and z:
                        zero+=1

                    elif flag and o:
                        one+=1
                print(y,x,flag,one,zero)
        print()        
        nn=nn//2
        if nn<1:
            return one,zero


n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
blue,white = play()
print(white)
print(blue)