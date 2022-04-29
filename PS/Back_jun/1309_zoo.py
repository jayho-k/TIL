n = int(input())

total = 1
if n == 1:
    print(2)

else:
    memo_num1 = 1
    for i in range(n-1,0,-1):
        memo_num1*=(i+1)
        total += memo_num1

    print(total%9901)
