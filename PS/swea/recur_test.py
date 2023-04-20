

def recur(n):
    if n<=0:
        print('somthing')
        return 10
    else:
        print(n)
        return recur(n-1) + 1

print(recur(10))





# def recur(n):
#     if n<=0:
#         return 0
#     print('val :',n)
#     return recur(n-1)-recur(n-2)

# recur(5)
