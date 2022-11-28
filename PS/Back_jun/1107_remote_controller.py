'''
5457
3
6 7 8

예제 1의 경우 5455++ 또는 5459--

'''

n = int(input())
m = int(input())
if m == 0:
    break_lst = []
else:
    break_lst = list(map(int,input().split()))
    

target_lst = list(map(int,list(str(n))))
c = 100

not_break = [i for i in range(10) if i not in break_lst]
tmp1 = [-1]*(len(target_lst))
tmp2 = [-1]*(len(target_lst))

state1 = True
state2 = True

for t in range(len(target_lst)):
    for i in range(9,-1,-1):
        if state1== True:
            if i in not_break and i < target_lst[t]:
                tmp1[t] = i
                state1 = False
                break

            elif i in not_break and i == target_lst[t]:
                tmp1[t] = i
                break

        else:
            tmp1[t] = not_break[-1]

    for j in range(10):
        if state2==True:
            if i in not_break and i > target_lst[t]:
                tmp2[t] = i
                state1 = False
                break

            elif i in not_break and i == target_lst[t]:
                tmp2[t] = i
                state2 = False
                break

        else:
            tmp2[t] = not_break[0]

# print(not_break)
# print(tmp1)
# print(tmp2)
# print(num)
a1 = a2 = 1e9
if n == 100:
    print(0)
else:
    if -1 not in tmp1:
        num1 = int(''.join(list(map(str, tmp1))))
        a1 = n-num1
        if a1 < 0:
            a1 = 1e9

    if -1 not in tmp2:
        num2 = int(''.join(list(map(str, tmp2))))
        a2 = num2-n
        if a2 < 0:
            a2 = 1e9
    
    a = min(a1,a2)
    print(a + len(target_lst))