
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
# 두명 찾아야함

tall = [int(input()) for _ in range(9)]

sm = sum(tall)
re = sum(tall)

def find():
    global sm
    global re
    for i in range(len(tall)):
        for j in range(i+1, len(tall)):
            sm = sm-tall[i]-tall[j]
            if sm == 100:
                return i,j

            else:
                sm = re

i,j =find()
lst = []
for k in range(len(tall)):
    if k == i or k == j:
        continue
    lst.append(tall[k])

lst.sort()
for i in lst:
    print(i)