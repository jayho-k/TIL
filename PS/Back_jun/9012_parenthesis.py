'''
조건이 총 몇개인지부터 파악을 해줘야한다
1. (    2.  )   ==> 이렇게 2개만 파악해주면 가능

1. ( 가 들어오는 경우
2. ( 이거 다음에 )가 들어오는 경우
3. ) 가 들어는 경우

방법
1. 리스트에 다 넣어
2. for문으로 세
3. 리스트1을 만들고 거기에 ( 가 들어오면 냅둬

4. ( 이거 다음에 ) 이게 들어오려고 해 ==> ( 이거 없애
5. 안에 아무것도 없어 그런데 ) 이게 들어오려고 해 ==> break

6. 리스트안에 아무것도 없어 ==> 그럼 YES , 아니면 NO
'''

n = int(input())
for i in range(n):
    lst = list(input())
    lst1 = []

    for i in range(len(lst)):
        if lst[i] == '(':
            lst1.append(lst[i])

        elif lst[i] == ')':
            if lst1 == []:
                lst1.append(1)
                break

            elif lst1[-1] == '(':
                lst1.pop()

    if lst1 == []:
        print('YES')

    else:
        print('NO')


    


