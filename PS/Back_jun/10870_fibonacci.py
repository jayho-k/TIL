'''
10

'''


def fib(d):


    if d == 0:
        return 0
    if d == 1:
        return 1

    return fib(d-2) + fib(d-1)

n = int(input())
s = fib(n)
print(s)