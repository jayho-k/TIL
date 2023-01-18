

# 01_Abnormal

> 1. **anomaly**?
> 2. **Insertion anomaly**
> 3. **Deletion anomaly**
> 4. **Update anomaly**

출처

https://developer-talk.tistory.com/256

https://1000hg.tistory.com/22



## 1. anomaly?

**이상현상이란?**

- 테이블내의 데이터 중복성에 의해서 발생되는 **데이터 불일치 현상**



**정규화를 사용해야하는 이유**

- 데이터베이스에서 **정규화를 수행하지 않으면**, 데이터의 중복이 발생하고 전체적으로 **무결성이 저하**된다.
- 즉 이상현상으로 인해 현실세계의 **실제 값과 데이터베이스에 저장된 값이 일치하지 않는 문제**가 발생
- 이것을 **이상 현상**이라고 한다.



**이상현상의 종류**

- Insertion anomaly
- Deletion anomaly
- Update anomaly



## 02_Insertion anomaly

> 삽입 이상

**Insertion anomaly**

- **특정 데이터가 존재하지 않아** 중요한 데이터를 데이터베이스에 **삽입할 수 없을 때** 발생

![image-20230118175204650](C:\Users\jayho\AppData\Roaming\Typora\typora-user-images\image-20230118175204650.png)

- 수학과가 신설 되었다
- 하지만 아직 신입을 받지 않았기 때문에 테이블에 값을 추가할 수 없음
- 따라서 정규화를 통해서 학과 테이블을 나눠야 한다. (제 3정규화?)



## 03_Deletion anomaly

> 삭제 이상

- **특정 정보를 삭제**하면, **원치 않는 정보도 삭제**되는 현상

![image-20230118175717985](C:\Users\jayho\AppData\Roaming\Typora\typora-user-images\image-20230118175717985.png)

- 둘리가 자퇴
- 둘리가 학과에 한명 밖에 없음
- 따라서 학과장 코드가 사라짐
- 이때도 정규화를 통해서 테이블을 나눠주어야 한다.





## 04_Update anomaly

> 갱신 이상

- 테이블의 **특정 데이터를 업데이트**했는데, **정상적으로 변경되지 않은 경우** 그리고 **너무 많은 행을 업데이트**하는 것

![image-20230118180128214](C:\Users\jayho\AppData\Roaming\Typora\typora-user-images\image-20230118180128214.png)

- 상황 : 학과장 이름 개명 => 학과장명을 변경해야함
- 학과생이 1000명일 경우 1000개의 데이터를 변경해야하는 비효율이 발생
- 제 1정규화를 통해서 해결

























