s = 10001
lst = list(range(1,s))
for num in range(1,s):
    num1 = str(num)
    num_lst = list(map(int, num1))
    sum_num = num + sum(num_lst)

    if sum_num in lst:
        lst.remove(sum_num)
        
for i in lst:
    print(i)
