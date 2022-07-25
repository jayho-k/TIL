'''
4
123 1 1
356 1 0
327 2 0
489 0 1


'''

n = int(input())

hint = []

for _ in range(n):
    num,s,b = input().split()
    num_lst = list(map(int,list(num)))
    s = int(s)
    b = int(b)
    hint.append(num_lst,s,b)


for i in range(100,1000):

    i = str(i)
    lst_i = list(map(int,list(i)))


    
