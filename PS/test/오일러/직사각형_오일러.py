'''
1 0 4 2
8 3 9 4
2 3 5 7
4 6 7 8
3 1 6 5
1 8 4 10
7 2 9 5
8 8 10 9
1 4 2 6
'''

    
from sys import stdin
stdin = open("오일러\input.txt")

store = set()
lst = []
while 1:
    s = stdin.readline().rstrip('\n')
    if s=='':
        break
    x1,y1,x2,y2 = map(int,s.split())
    # lst.append((x1,y1,x2,y2))
    for y in range(y1,y2):
        for x in range(x1,x2):
            if (y,x) not in store:
                store.add((y,x))
# print(lst)
print(len(store))