# 자바란?

![image-20240713155731195](./basic.assets/image-20240713155731195.png)

- 자바는 표준 스펙을 기반으로 만들어져야한다.



![image-20240713160048817](./basic.assets/image-20240713160048817.png)

- 자바 프로그램은 컴파일과 실행단계를 거침
  1. **Hello.java와 같은 자바 소스코드를 개발자가 작성**
  2. **자바 컴파일러를 사용해 소스코드를 컴파일**
     - javac라는 프로그램을 사용
     - .java => .class 파일이 생성
     - 자바 소스 코드를 바이트코드로 변환 =. JVM에서 더 빠르게 실행될 수 있게 최적화하고 문법오류를 검출
  3. **자바 프로그램 실행**
     - 자바가 제공하는 java라는 프로그램 사용
     - JVM이 실행되면서 프로그램 작동



## 변수

**리터럴 타입 지정**

- 정수 리터럴은 int를 기본으로 사용한다.
- 따라서 int 범위까지 표현할 수 있다.
- 숫자가 int 범위인 20억을 넘어가면 L을 붙여서 long으로 변경해야한다.
- 실수 리터럴은 double을 사용하고 float형을 사용하려면 f를 붙인다.



**실무에서 많이 사용하지 않는 변수들**

- byte : 표현 길이가 너무 작다.  자바는 기본으로 4byte(int)를 효율적으로 계산하도록 설계되어 있다.! int를 사용하자
  - byte 타입을 직접 선언하고 숫자 값을 대입해서 계산하는 일이 거의 없음
  - **대신 파일을 바이트 단위로 다루기 때문에** 파일 전송, 파일 복사 등에 주로 사용
- short : 표현 길이가 너무 작음. int를 사용하자
- float : 표현 길이와 정밀도가 낮다. 실수형은 double을 사용하자
- char : 문자하나를 표현할 일이 없다. 문자 하나를 표현할 때도 문자열을 사용할 수 있다.

- 메모리 용량은 매우 저렴하다. 따라서 메모리 용량을 약간 절약하기 보다는 개발 속도나 효율에 초점을 맞추는것이 효과적



**변수 규칙**

- 변수 이름은 숫자로 시작 x
- 공백 x
- 영문, 숫자, 달러, 밑줄만 가능

관례

- Camel case, 소문자 시작

클래스 : 대문자 OrderDetail

패키지 : 소문자 org.spring.boot

상수 : 대문자 USER_LIMIT



## 연산자

- 문자열 비교
  - ==이 아니라 .eaquls() 메서드를 사용해야한다.



## 조건문

- condition 조건이 서로 관련이 없는 독립 조건이라면 else if를 사용하지 않는 것이 좋음

```java
if (condition1);
else if (condition2);

if (condition1);
if (condition2); // 이런식으로 나눠서 가는 것이 좋다.

```



- 일반적으로 명령이 한개만 있을 경우에도 중괄호를 사용하는 것이 좋다.
  - 가독성 : 더 읽기 쉽게 만들어 준다.
  - 유지보수성 : 코드를 추가할 경우 에러가 날 가능성 존재



## Switch





















