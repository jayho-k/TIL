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

def check(i,j,n):
    
    zero = 0
    one = 0
    for y in range(i,i+n):
        for x in range(j,j+n):
            if grid[y][x]==1:
                one+=1
            else:
                zero+=1
    
    if zero and one:
        return 0,0
    
    else:
        return zero,one


def play(y,x,n):

    global white
    global blue

    zero,one = check(y,x,n)

    if zero:
        white += 1
    
    elif one:
        blue += 1
    
    # 나누기
    else:
        nn = n//2
        play(y,x,nn)
        play(y+nn,x,nn)
        play(y,x+nn,nn)
        play(y+nn,x+nn,nn)

n = int(input())
grid = [list(map(int,input().split())) for _ in range(n)]
white = 0
blue = 0
play(0,0,n)

print(white)
print(blue)



# def check(y,x,nn):
#     z = 0
#     o = 0
#     store = set()
#     for yy in range(y,y+nn):
#         for xx in range(x,x+nn):
#             store.add((yy,xx))
#             if z and o:
#                 return False,0,0,set()

#             if grid[yy][xx]==1:
#                 o+=1
#             else:
#                 z+=1
#     if z and o:
#         return False,0,0,set()
#     return True,z,o,store

# def play():

#     nn = n
#     store = set()
#     one,zero = 0,0
#     while 1:
#         for y in range(0,n,nn):
#             for x in range(0,n,nn):
                
#                 if (y,x) not in store:

#                     flag,z,o,store_tmp = check(y,x,nn)
#                     store|=store_tmp
#                     if flag and z:
#                         zero+=1

#                     elif flag and o:
#                         one+=1
#                 print(y,x,flag,one,zero)
#         print()        
#         nn=nn//2
#         if nn<1:
#             return one,zero


# n = int(input())
# grid = [list(map(int,input().split())) for _ in range(n)]
# blue,white = play()
# print(white)
# print(blue)