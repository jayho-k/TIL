'''
24 18

'''

n1, n2 = map(int,input().split())

n = 2
gcd = 1
while 1:
    
    if n1%n==0 and n2%n==0:
        gcd *= n
        n1 = n1//n
        n2 = n2//n
    else:
        n+=1

    if n > n1 or n>n2:
        lcd_sub = n1*n2
        break
    
lcd = lcd_sub*gcd

print(gcd)
print(lcd)

