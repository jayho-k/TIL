'''
quqacukqauackck


'''


s = input()

duck = 'quack'
duck_lst = list(duck)
table = [0]*5



for i in s:
    if i == 'q':
        table[0] += 1

    elif i == 'u' and table[0]!=0:
        table[0] -= 1
        table[1] += 1

    elif i == 'a' and table[1]!=0:
        table[1] -= 1
        table[2] += 1

    elif i == 'c' and table[2]!=0:
        table[2] -= 1
        table[3] += 1

    elif i == 'k' and table[3]!=0:
        table[3] -= 1
        table[4] += 1

print(table)