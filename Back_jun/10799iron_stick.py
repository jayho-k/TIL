# ()(((()())(())()))(())
# 17
'''
## 풀이참조 함

## 자료구조는 처음에 조건이 총 몇개가 있는지 세는 것부터 해야한다
즉: 1. (   2. ()   3. )  --> 그리고 하나씩 어떤 조건에서 만족을 시키는지 따져주어야 한다

1. ( 가 나올시 stack을 쌓아올린다
2. ()가 나오면 개수를 세고 스텍 개수를 하나 뺀다
3. )가 나오면 마지막 막대의 수를 센다 + 1을 해해주고 스택수를 하나 뺀다
'''

lst = list(input())
stack = []
cnt = 0

for i in range(len(lst)):
    
    if lst[i] == '(':
        stack.append(i)

    elif lst[i-1] == '(' and lst[i] == ')' :
        stack.pop()
        cnt += len(stack)

    else:
        stack.pop()
        cnt += 1

print(cnt)
