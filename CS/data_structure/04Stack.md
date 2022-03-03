# Stack

- 스택에서
  - push (넣고)
  - pop (빼고)
  - 파이썬을 리스트에서 비슷하게 만들어낼 수 있다.
  - 곧바로 쓰지 않는이유: 딱 두가지 연산을 통해서만 할 수 있다
  - 실수로 다른 함수를 이용해서 스택에 값에 관여하게 된다.
  - 따라서 이러한 class를 만들어서 사용하게 된다.

```python
class Stack:
    
    def __init__(self):
        self.items = []         # 데이터 저장을 위한 리스트 준비
        
    def push(self, val):
        self.items.append(val)
        
    def pop(self):
        try:
            return self.items.pop()   # pop할 아이템이 없으면 인덱스에러 발생
        except IndexError:
            print("stack is empty")
            
    def top(self):
        try:
            return self.items[-1]  # 가장 위에 있는 값을 알고 싶을 때 사용
        except IndexError:
            print('stack is empty')           
            
    def __len__(self):
        return len(self.items)   # len() 로 호출하면 stack의 item수 반환
    
    
s = Stack()
s.push(10)  # 10이 들어가게 된다. [10]
s.push(2)
s.pop() # 2가 지워지고 반환


```



예1) 괄호 맞추기

```python
# (2+5)*7 - ((3-1)/2 +7)
# 쌍인줄 알아 맞춰야 함 = True

# 관찰
s = Stack()
for p in parseq:
    if p == '(':
        s.push(p)
    elif p ==')':
        s.pop()
        
    else:
        print('Not')
    
if len(s > 0):
    return False
else:
    return True
```



예2) 계산기 코드 작성

- 피연산자, 연산자 ==> 토큰(token)
- 먼저 피연산자, 연산자를 구분해 주어야한다.
  - 이항 연산자 (이것만 있다고 가정)
    - 2+3 오터레이터가 피연산자 2개를 원함
  - 단항 연산자
    -  \+ 3 - 6  ==> 피 연산자 하나만 필요함

infix ==> postfix 수식으로 바꾸기

- 2+3*5 (infix 수식)  ==> 2 3 5 * + (postfix수식) 으로 바꿀 것이다.
  1. 괄호치기 (2+(3*5)
  2. 연산자의 오른쪽 괄호 다음으로 연산자 이동
  3. 괄호 지우기 ==>  2 3 5 * +
- 3 * (2 + 5) * 4
  1. 괄호치기 ((3 * (2 + 5)) * 4)
  2. 연산자의 오른쪽 괄호 다음으로 연산자 이동
  3. 괄호 지우기 ==>  3 2 5 + *  4  * 

```python
'2+3*5' # 입력으로 받음
'(2+(3*5))' # 이런식으로 계산이 되어야 한다.
# 입력: + - * / ( ) 숫자로 구성
# 출력: postfix로 수식
# 1. 피연산자의 순서는 그래도
# 2. 연산자는 다른 연산자를 봐야한다. ==> 우선순위를 보고 언제 나올지를 결정
# 2-1 우선순위가 자기보다 높아 => 그럼 기달 어디서?? 스택에서 기다린다 ==> 언제나갈지 결정
# 2-2 우선순위가 자기보다 낮아

# a*b+c ==> a b * c + 
# (a+b)*c ==> a 
# stack = [(, +, ]  오른쪽 괄호가 나오면 왼쪽 괄호가 나올때 까지 pop
# [ * ]
# 오른쪽 괄호가 나올때 까지는 기다린다 (오른쪽 괄호는 우선순위가 제일 높음)
# 왼쪽괄호는 우선순위가 제일 낮음
# a b + c *

# 리스트: outstack
# 스택 : opstack
# for each token in expr:

for token in expr:
    if token == operand:
        outstack.append(token)
    elif token == '(':
        opstack.push(token)
        
    elif token == ')':
        opstack에 저장된 연산자를 다 pop한다 ( 가 나올때 까지
        ==> outstack에 append
    
    elif token in 사칙연산:
        opstack에 token보다 우선순위 높은 연산자 모두 pop, 자신이 push
                                   
    opstack에 남은 연산자 모두 pop ==> outstack                               
```





```python
'''
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
```





























