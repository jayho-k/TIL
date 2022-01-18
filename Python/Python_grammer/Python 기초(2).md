# Python 기초(2)

## 제어문

### 조건문(if)

- True/ False 정할 때 사용
- **input()** ==> 무조건 **string** ==> int()를 해주어야 한다.



### 복수 조건문(elif)



 ### 중첩 조건문

```py
if:
	if:
	else:
	
	
```

중첩이 가능하다



### 조건 표현식



- 절대값을 표현하는 법 (파이썬의 신기한 버전)

```python
value = num if num >= 0 else -num
# 만약에 num이 0이상으면 value = num
# 만약에 num이 0보다 작으면 - num을 해라
```

​		간단한 조건에 따라 값을 넣을 때 사용한다.



- 동일하게 표현하기 

  ```python
  num = 2
  if num % 2:
  	result = '홀수'
  else:
      result = '짝수'
      
      # 표현식 버전
      result = '홀수' if num % 2 else '짝수'
      
  num = -5 
  valuse = num if num >= 0 else 0
  print(value)
  
  if num >= 0:
      value = num
      print(value)
  else:
      value = 0
      print(value)
  ```

  

### 반복문

### while

- **조건이 참**일경우 사용
- **종료조건**이 반드시 필요



- 몇번 반복될까?

```python
a = 0
while a < 5:
    print(a)
    a += 1
print('end')
```

0 1 2 3 4 ==> 총 5번 실행이 된다.

python tutor라는 사이트에서 몇번 실행되는지 알 수 있다

링크 : https://pythontutor.com/visualize.html#mode=edit



### for 문

1. 

```python
for i in 'something':
    print(i)
    # 하나씩 s o m e ..... 출력하게된다.
```

2. 

``` python
chars = 'something'
for i in range(len(chars)):
    print(chars[i])
```

3. 딕셔너리 순회

``` python
# 0. dictionary 순회 (key 활용)
for key in dict:
    print(key)
    print(dict[key])


# 1. `.keys()` 활용
for key in dict.keys():
    print(key)
    print(dict[key])


# 2. `.values()` 활용
# 이 경우 key는 출력할 수 없음
for val in dict.values():
    print(val)


# 3. `.items()` 활용
for key, val in dict.items():
    print(key, val)
```

![image-20220117151642673](Python 기초(2).assets/image-20220117151642673.png)

![image-20220117151743730](Python 기초(2).assets/image-20220117151743730.png)

``` python
grades = {'kim' = 80, 'lee' : 100}

for key in grades:
    print(key, grade[key])

# 2. key     
for key in grades.keys():
    print(key, grade[key])
   
# 3. 벨류 뽑기
for value in grades.values():
    print(key, grade[key])  
    
# 4. items (둘다 뽑기)
for key, value in grades.itmes():
    print(key, value)
    
    
```



4. enumerate 순회

- (인덱스, 해당하는 것) 을 튜플로 묶어준다.

- enumerate로 반환 ==> 따라서 list로 묶어준다.

```python
list(enumerate(members, start = 1))
# 이렇게 시작을 정할 수 있다.
```



5.  list comrpehension

- 리스트로 만들때 한줄로 만들기

```python
# list로 한줄로 만들기

[i for i in lst]
[i**3 for i in lst]

[i for i in lst if]

# 1~30까지 숫자 중에 홀수만 출력 = 리스트 형태로
f = [ i for i in range(1,31) if i % 2 == 1 ]
print(f)
```





6.  Dictionary comrpehension

- 리스트로 만들때 한줄로 만들기

``` python
key: value for (변수) in <iterable>
key: value for (변수) in <iterable> if <조건>
```

![image-20220117153333493](Python 기초(2).assets/image-20220117153333493.png)

## 반복문 제어

- break
- continue
- for - else

### break

- 특정 조건에 반목문을 종료 시키기 위해서는 **break**

- 



### continue

- continue를 만나면, 이후 코드인 print(i)가 실행되지않고 다음 반복

```python
for i in range(6):
    if i % 2 == 0:
        continue
    print(i)
	
    # 1 3 5
    # 짝수인 경우에는 그냥 넘어가~~~ 라는 뜻
```



### else

- 즉, for 문이 끝까지 돌았는지를 알아보기 위한 것
- else문은 break로 중단 되었는지 여부에 따라 실행
- else는 자주 if - break와 같이 사용된다

![image-20220117154412181](Python 기초(2).assets/image-20220117154412181.png)



![image-20220117154822336](Python 기초(2).assets/image-20220117154822336.png)

### pass 와 continue 차이

- 예시)

![image-20220117155037424](Python 기초(2).assets/image-20220117155037424.png)

![image-20220117155022049](Python 기초(2).assets/image-20220117155022049.png)

- pass는 그냥 구조만 잠시 짜놓을 때 사용한다. 기능적으로는 잘 사용하지 않음





