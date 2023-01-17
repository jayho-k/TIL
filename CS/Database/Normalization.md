# Normalization

> 01_Normalization?
>
> 02_단계별 정규화 절차

출처 : 

https://code-lab1.tistory.com/48

https://github.com/Youji-Sung/CS-study/tree/master/%EB%8B%A4%EC%9D%B8



## 01_Normalization?

테이블 간의 중복된 데이터를 허용하지 않는 것

- **정규화 X :**
  - 데이터의 중복이 많아져 트랜잭션에서 중복된 데이터를 모두 변경해야 하므로 
    성능이 떨어지게 됨
- **정규화가 과할 경우**
  - 데이터를 가져올 때 조인이 많이 필요하게 됨



## 02_단계별 정규화

> 1NF , 2NF , 3NF
>
> BCNF (Boyce-Codd Normal Form)
>
> 4NF, 5NF

#### 1NF

![image-20230115184737488](C:\Users\jayho\AppData\Roaming\Typora\typora-user-images\image-20230115184737488.png)

문제점

- 자바 수강신청 한 사람 찾기 어려워진다. 
  (search가 힘들어짐 하나씩 다 확인을 해주어야하기 때문)
- 프로그램 수정이 어려워진다.



![image-20230115185039871](C:\Users\jayho\AppData\Roaming\Typora\typora-user-images\image-20230115185039871.png)

**제1정규화**

- **한 칸에 하나의 데이터**만 넣어준다.
- 릴레이션의 모든 속성 값이 **원자값**을 갖는 경우



**규칙**

```
- 각 컬럼이 하나의 속성만을 가져야 한다.
- 하나의 컬럼은 같은 종류나 타입(type)의 값을 가져야 한다.
- 각 컬럼이 유일한(unique) 이름을 가져야 한다.
- 칼럼의 순서가 상관없어야 한다.
```

















