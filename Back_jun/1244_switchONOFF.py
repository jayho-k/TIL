'''



1. 스위치를 받는다
2. 남자와 여자를 나눠준다
2-1
남자일 경우
받은 수의 배수부분의 숫자를 바꿔준다
(리스트를 만들어서 [(배수xn)-1]번째를 바꿔준다)

2-2
여자일 경우
받은 수를 중심으로 좌우가 대칭인 만큼 스위치를 바꾼다
중심으로 한칸씩 같은지를 확인하면 된다.
반복문으로 점차 늘려가야한다.

예를 들어 받은 수가 3이야
중심 = lst[n - 1]
n-2 와 n을 비교
n-3 과 n+1과 비교 등등
앞부분 ==> 0이 되거나 뒷부분이 len(lst)값이 된다면
break를 걸어줘야 한다 

3을받음
front = 2
back = 2
cnt = 0
for i in range(len(배열//2 + 1)):
    cnt += 1
    if lst[front-1] == lst[back+1]:
        front -=1
        back +=1
    elif lst[front-1] != lst[back+1]:
        받은 수를 기준으로 숫자를 전부 바꾸어 주어야 한다.
'''


'''
8
0 1 0 1 0 0 0 1
2
1 3
2 3

20
1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1

10
0 1 1 0 0 1 1 0 1 1  
4
1 3  ==> 0 1 0 0 0 0 1 0 0 1
2 3  ==> 0 1 1 0 0 0 1 0 0 1
1 3  ==> 0 1 0 0 0 1 1 0 1 1
2 3  ==> 0 1 1 0 0 1 1 0 1 1
'''
num_swch = int(input())  # 10
swch = list(map(int, input().split()))
num_ppl = int(input())

for _ in range(num_ppl):
    sx, num = map(int, input().split())  # 7

    if sx == 1:
        for i in range(1, (len(swch)//num) + 1):
            if swch[(i*num) - 1] == 0:  
                swch[(i*num) - 1] = 1

            elif swch[(i*num) - 1] == 1:
                swch[(i*num) - 1] = 0


     # swch = 40 num = 1   /  f = -1  c = 0  b = 1  => 비교대상이 없음==> c 만 변함
     # num = 2/ f = 0  c = 1  b = 2

    else:
        front = num - 2
        crnt = num -1   
        back = num
        
        if swch[crnt] == 1:
            swch[crnt] = 0

        elif swch[crnt] == 0:
            swch[crnt] = 1

        while front >= 0 and back <= len(swch)-1:
 
            if swch[front] == swch[back]:
        
                if swch[front] == 1:
                    swch[front] = 0
                    swch[back] = 0

                elif swch[front] == 0:
                    swch[front] = 1
                    swch[back] = 1

                front -=1
                back +=1

            elif swch[front] != swch[back]:
                break

            
lst = list(map(str, swch))
s = 0
e = 20
while s < len(lst):

    print(' '.join(lst[s : e]))

    s = e
    e += 20

        # 받은 수를 기준으로 숫자를 전부 바꾸어 주어야 한다.
