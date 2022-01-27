# num = int(input())
'''
1. 100이 들어옴
2. 하나씩 해보자 .ex) 100 99 1// 100 1 99 -98
    식: 들어온수 - i = a1
        i - a1 = a2
        a2 - a3 = a4
        ex)
        100 - 60 = 40
        60 - 40 = 20
        40 - 20 = 20


    초기 값: 100
    next 값: i 
    초기, next = next, 초기 - next

3. 마이너스가 나오면 스탑
4. 그 전까지의 수를 리스트에 넣고 셈
5. 그것을 센것이 mx보다 크면 그것으로 넘어감
6. 멕스와 리스트를 출력
'''
num = int(input())
rlst = []
mx_len = 0

for i in range(num+1):

    lst = [num,i]
    c = 0
    while 1:
        lnum= lst[c] - lst[c+1]
        if lnum < 0:
            break
        lst.append(lnum)
        
        if mx_len < len(lst):
            mx_len = len(lst)
            rlst = lst
        c += 1

print(mx_len)
print(' '.join(map(str,rlst)))


