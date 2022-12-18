'''
4
123 1 1
356 1 0
327 2 0
489 0 1

'''

n = int(input())


play = []
for i in range(n):
    num,s,b = input().split()
    lst = list(map(int,list(num)))
    s = int(s)
    b = int(b)
    play.append([lst,s,b])



for i in range(100,1000):
    i = str(i)
    i_lst = list(map(int,list(i)))

    play = []

    for p in play:
        p_lst,s,b = p






