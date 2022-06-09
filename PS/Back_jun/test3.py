'''
20
7
23
19
10
15
25
8
13
'''
total = 0
lst = []
for i in range(9):
    tmp = int(input())
    total += tmp
    lst.append(tmp)

lst.sort()
lier = total -100
strt = 0
end = len(lst)-1

while strt <= end:

    if lst[strt]+lst[end] < lier:
        strt += 1
    
    elif  lst[strt]+lst[end] > lier:
        end -= 1
    
    else:
        lst[strt]
        lst[end]
        break


for i in range(len(lst)):
    if i == strt or i == end:
        continue
    print(lst[i])


