'''
3
0
1
3


'''

z = [1,0,1]
o = [0,1,1]
fi = [1,1]

def fibo(n):
    if n==0:
        return 0
    elif n==1:
        return 1
    
    for i in range(2,n+1):
        fi.append(fi[i-1]+fi[i-2])

fibo(40)
print(fi)



# def fib(n):
#     l = len(z)
#     if n>= l:
#         for i in range(l,n+1):
#             z.append(z[i-1]+z[i-2])
#             o.append(o[i-1]+o[i-2])
# fib(40)
# for _ in range(int(input())):
#     n = int(input())
#     print(z[n],o[n])
