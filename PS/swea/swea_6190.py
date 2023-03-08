'''

1
4
2 4 7 10

'''
def find_increase(a): 
    
    while 1:
        equ = a//10
        rem = a%10
        if equ == 0:
            return True
        
        if equ%10 <= rem:
            a = equ
        else:
            return False


for tc in range(1,int(input())+1):
    n = int(input())
    lst = list(map(int,input().split()))
    mx = 0
    for i in range(n):
        for j in range(i+1,n):
            a = lst[i]*lst[j]
            if find_increase(a):
                mx = max(mx, a)
    if mx==0:
        print(f"#{tc} -1")
    else:
        print(f"#{tc} {mx}")
    