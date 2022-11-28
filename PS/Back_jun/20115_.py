'''
Energy Drink

5
3 2 10 9 6

10
100 9 77 65 39 27 45 1 80 495
'''
n = int(input())
lst = list(map(int,input().split()))

lst.sort(reverse=True)
# print(lst)

tmp = 0

for i in range(len(lst)):
    if tmp == 0:
        tmp = lst[i]
    else:
        tmp += lst[i]/2


print(tmp)

