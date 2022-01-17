# Python 기초

- 스타일 가이드 : PEP8

## 문법

### 변수(Variable)

- 이름 = 값 (등호 1개 => 할당)
- 객체(ocject) = things(무언가)
- 변수 활용에 중요한 점 == 타입(type)



### 변수 연산

- 숫자 + 숫자 가능
- 문자 + 문자 가능



### 변수 할당

![image-20220117092510164](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220117092510164.png)

typeerror (unpack) : 풀 이름이 부족하다

too many 				:  변수가 너무 많음



## 자료형

![image-20220117093944606](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220117093944606.png)

### 불린(Boolean)

![image-20220117094131666](Python 기초.assets/image-20220117094131666.png)



### 정수(int)

- 특징: overflow가 발생하지 않는다.

- 진수 (b, o, x)

  - 2진수: 0b     ex)  ob10 --> 2

  - 8진수 : 0o    ex)  0o30 --> 24

  - 16진수: 0x   ex)  0x10 --> 16



### 실수(Float)

- 특징 : rounding error

  - ![image-20220117094838096](Python 기초.assets/image-20220117094838096.png)

  - 해결: 절대값을 씌워서 굉장히 작은 수라면 rounding 에러라고 판단한다. 



## 문자열(String Type)

- immutable(변하지 않음) : str 의 일부분만 바꿀 수 없다.
- Iterable(반복가능)  :  for 문에서 순서대로 표현가능

![image-20220117100435610](Python 기초.assets/image-20220117100435610.png)



### Escape sequence

![image-20220117100518539](Python 기초.assets/image-20220117100518539.png)

### String Interpolation

- 문자열 사이에 변수를 넣는다

![image-20220117100916283](Python 기초.assets/image-20220117100916283.png)



![image-20220117101227557](Python 기초.assets/image-20220117101227557.png)



## 컨테이너(Container)

- 분류 : 순서가 있는 데이터 vs 순서가 없는 데이터

  ![image-20220117101421153](Python 기초.assets/image-20220117101421153.png)



### 리스트(list)

- list[-1] : 끝에 값을 의미한다.
- boxes = ['a','b',['apple', 'banana', 'cherry']]
- boxes[- 1] [1] [0]          # 'b'  



### 튜플(Tuple)

- 불변 ==> 변경이 불가능
- x, y = 1, 2    ==    x, y = (1, 2)   :  파이썬 내부적으로 tuple로 처리한다



### 레인지 (Range)

-  range(n, m, s): n ~ m-1 을 s만큼 증가
- s => -1   가능
- n > m    가능



### Packing/ Unpacking Operator

​	*을 사용한다.

![image-20220117103345223](Python 기초.assets/image-20220117103345223.png)

 	**packing은 list로 저장된다. **



![image-20220117103402110](Python 기초.assets/image-20220117103402110.png)

​           **각각이 흩어져서 들어간다!! 라는 뜻임**



### 셋(Set)

- 집합이랑 비슷하다.
- set( ) or { }중괄호를 사용한다. 
- {1,2,3,1,2}       # {1,2,3}

- **주의 :** 
  - {}: 빈 중괄호 = 딕셔너리 // 만약 **빈 set**을 원하면 ==> **set()**
  - **순서가 필요할 경우 사용 x**



### 딕셔너리(Dictionary)

- 키 - 값(key - value)
- **key**에 **list 불가**   ///  **value**에 **list 가능**
- 순서 없음





## 형 변환(Typecasting)



### 자료형 변환

- 암시적 형 변환(Implicit) : 사용자 의도 x, 파이썬 내부에서 변환

![image-20220117104614729](Python 기초.assets/image-20220117104614729.png)

​		**int와 float 연산 ==> 무조건 float**



- 명시적 형 변화(Explicit) : 

​		그냥 형태를 맞추기 위해서 변환을 시켜주는 것 ex) int() ==> str()

![image-20220117105039110](Python 기초.assets/image-20220117105039110.png)

![image-20220117105100976](Python 기초.assets/image-20220117105100976.png)

​			만약 float('3/4') + 5.3을 하고 싶다면

​			a = '3/4' , float(a) + 5.3이면 가능



### 컨테이너 형 변환

![image-20220117110144214](Python 기초.assets/image-20220117110144214.png)

dictionary를 list로 변환 ==> key만 나옴



## 연산자(Operator)

### 산술연산자

- divmod ==> 튜플로 반환 (몫, 나머지)



### 논리 연산자

- and : 모두 True 일때만 True
- or : 모두 False 일때만 False

![image-20220117110917427](Python 기초.assets/image-20220117110917427.png)

and : 3번쨋꺼 ==> 0이 False ==> 0

or :  4번쨋꺼 ==> 5가 True ==> 5



### 멤버십 연산자

- in
- not in



### 시퀀스형 연산자

- '12' + 'b'     ==> '12b'

- (1, 2) + ('a', )  ==> (1, 2, 'a')

  

### 슬라이싱(Slicing)

![image-20220117111722459](Python 기초.assets/image-20220117111722459.png)

​						미포함이라고 하더라도 에러가 뜨지 않는다	

​				

![image-20220117111744381](Python 기초.assets/image-20220117111744381.png)





![image-20220117111945262](Python 기초.assets/image-20220117111945262.png)



### set 연산자

![image-20220117112021839](Python 기초.assets/image-20220117112021839.png)

### 프로그램 구성 단위

- **식별자 **  : 이름

- **리더럴 **  : 변수

- **문장**      : 실행 가능한 최소한의 코드 단위

- **함수 **     : 명령을 수행하는 함수 묶음

- **모듈 **      : 함수/클래스의 모름

- **패키지**    : 프로그램과 모듈 묶음

- **라이브러리 **: 패키지 모음

























