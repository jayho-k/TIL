"""
분할 정복

8
11110000
11110000
00011100
00011100
11110000
11110000
11110011
11110011

((110(0101))(0010)1(0001))
"""
from pprint import pprint

def check(n,y,x):
    one = 0
    zero = 0
    for yy in range(y,n+y):
        for xx in range(x,n+x):
            if grid[yy][xx]==1:
                one+=1
            else:
                zero+=1
    
    if one and zero:
        return False,0,0

    else:
        return True,one,zero


def divide(n,y,x):
    global ans
    flag,one,zero = check(n,y,x)

    if flag:
        if one:
            ans+='1'

        elif zero:
            ans+='0'
    else:
        ans += '('
        divide(n//2,y,x)
        divide(n//2,y,x+n//2)
        divide(n//2,y+n//2,x)
        divide(n//2,y+n//2,x+n//2)
        ans += ')'


n = int(input())
grid = [list(map(int,list(input()))) for _ in range(n)]
ans = ''
divide(n,0,0)
print(ans)