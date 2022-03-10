
y, x = map(int, input().split())

if y == 1:
    print(1)

elif y < 3:
    
    if x <= 7:
        print((x-1)//2 + 1)

    else:
        print(4)


elif x <= 6:

    if x>4:
        print(4)

    elif x <= 4:
        print(x)

else:
    print(x -2)