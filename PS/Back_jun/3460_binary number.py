'''
1
13
'''
T = int(input())

for tc in range(1,T+1):
    
    n = int(input())

    lst = []
    loc = 0
    while 1:
        mok = n//2
        namuzi = n%2
        if namuzi == 1:
            lst.append(loc)

        loc += 1
        n = mok
        if mok == 0:
            break

    print(*lst)



