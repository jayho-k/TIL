'''
7
3
7
5
2
6
1
4
'''
n = int(input())


tmp = [1]*n
line = [int(input()) for _ in range(n)]


for back in range(n):
    for front in range(back):
        if line[back] > line[front]:
            tmp[back] = max(tmp[back], tmp[front]+1)

print(n-max(tmp))
