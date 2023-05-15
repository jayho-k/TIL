'''



'''

def play(i):

    if i == 0:
        return 0
    
    elif i==1:
        return 1
    
    elif i%2 == 0:
        return play(i//2)

    else:
        return 1-play(i//2)


k = int(input())
print(play(k-1))
