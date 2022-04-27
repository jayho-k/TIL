# 01_JavaScript_intro

### 자바의 필요성

- 브라우저 화면을 동적으로 만들기 위하기 때문
- 브라우저를 조작할 수 있는 언어



## 1. Browser

### 브라우저에서 할 수 있는 일

- ##### DOM (document object model)조작

  - 문서 조작
  - Parsing 
    - 구문 해석, 분석

- ##### BOM 조작

  - 브라우저 조작
  - window

- ##### JavaScript Core



## 변수

- 선언 : 변수 지정
- 할당 : 값 넣어주기
- 초기화 : 선언된 변수에 처음으로 값을 저장하는 행위

### let

- 재할당 할 예정인 선언시 사용 ==> 예약하는 느낌
- 변수 재선언 불가능
- 가능

```javascript
let number = 10  // 할당
number = 10 // 재할당
console.log(number)
```

- 불가능

```javascript
let number = 10
let number = 50
```



### const

- 재할당 할 예정이 없는 변수 선언 시 사용
- 변수 재선언 불가능
- 재할당 불가능 => 즉 =이 안됨
- 불가능

```javascript
let number = 10  // 할당
number = 10 // 재할당 불가능
```

- 불가능

```javascript
let number = 10
let number = 50 //재선언
```



#### block scope

- if, for, 함수등의 중괄호 내부를 가리킴
- 즉 변수를 거기 안에서 만들면 안에서만 해결



### var

- 호이스팅되는 특성으로 인해 예기치 못한 문제 발생가능
  - 없어도 나중에 있다고 생각하고 그냥 넘기게 되는 상황
  - 즉 변수를 선언 이전에 참조할 수 있는 현상
- 따라서 var를 지향하고 있음 ==> 사용하지 않음



## 데이터 타입

### 원시 타입(Primitive type)

##### 종류

- 숫자

- 문자

- 불리언



##### 숫자 타입

- NaN: 산술 연산 불가 
  - => 에러를 내기 싫어함 => 에러대신에 NaN을 내보냄
  - 타입이 숫자임
- Infinity : 무한대
- -Infinity  : (-) 무한대



##### 문자열 타입

- backtick (``)으로 표현
- ${        } 형태로 삽입가능



##### undefined

- 변수의 값이 없을 나타내는 데이터 타입
- 변수 선언 이후 직접 값을 할당하지 않으면 자동으로 undefined가 할당됨
- 즉 개발자 의도 없음



##### null

- 변수의 값이 없음을 의도적으로 표현할 때
- 개발자 의도 있음





### 참조 타입(Reference type)

- objects
- Array
- Function
- 등등



## 연산자

#### ===

- 자바스크랩트에서 는 ===을 사용한다. 

#### 

#### 논리연산자

- && : and
- || : or

- ! : not



#### 삼항 연산자

- 항이 세개가 필요하다는 것

```javascript
console.log(true ? 1 : 2) // 1 맞으면 앞에꺼/ 
console.log(false ? 1 : 2) // 2 틀리면 뒤에꺼

const result = Math.PI > 4 ? 'Yes' : 'No' // ath.PI > 4이니?? true, false?
console.log(result)
//No
```





## 조건문

#### - if

- 파이썬과 동일



#### -  switch

- nation을 한번만 써주기 위해서
- 하지만 모든 case 뒤에 break를 써주어야 한다.
- 그냥 if문 쓰자

```javascript
const nation = 'Korea'

//d
switch(nation){
    case 'Korea':{
        console.log('안녕하세요')
        break
    }
    case 'Korea':{
        console.log('안녕하세요')
        break
    }
    default:{
        console.log('hello')
    }
}
```





## 반복문

- while
- for
- for in
- for of



### for

```javascript
// 조건을 계속 주어야 한다.
for (let i=0; i<10; i++){
    console.log(i)
}


// 배열을 뽑아오는 방법
const arr = [1,2,3]
for (let i=0; i<arr.length; i++){
    console.log(i)
}

//딕셔너리의 키를 순회할 때 사용
for (key in dict){
    //do something
}

//딕셔너리의 value를 순회할 때 사용
for (key in dict){
    console.log(value[key])
}

// 파이썬에서 for in 같은 느낌
const fruits = ['딸기','사과','수박']
for (let fruit of fruits){
    console.log(fruit)
}





```





## 함수

- 이런 식으로 시용

```javascript
// 방법 1
function add(num1, num2){
    return num1 + num2
}

// 방법 2 ==> 이것을 많이 사용 한다. 이유: hoist를 막기 위해
const add = function(num1,num2){
    return num1 + num2
}


// 많은 배열 넣기
const manyArr = function(num1,...ar2){
    return [num1,ar2]
}


```



##### 콜백 함수

- 함수의 인자로 함수를 사용할 수 있다
- 그냥 함수에다가 함수 넣을 수 있음



#### Arrow Function

```javascript
// 방법 1
const arrow1 = function(name){
    return 'hello, ${name}'
}

// 방법 2
const arrow2 = (name) => { return 'hello, ${name}' }

// 방법 3
const arrow3 = name => { return 'hello, ${name}' }

// 방법4
const arrow4 = name => return 'hello, ${name}'
```























