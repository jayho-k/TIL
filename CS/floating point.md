# floating point

- 실수를 저장하기 위한 형식
  - 단정도 실수(32비트)
  - 배정도 실수(64비트)
- ![image-20220323141000072](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220323141000072.png)

- 가수부 : 실수의 유효 자릿수들을 부호화된 고정 소수점으로 표현
- 지수부 : 실제 소수점의 위치를 지수 승으로 표현

![image-20220323141145460](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220323141145460.png)

- ex)
- 1001.0011
  - 0001.0010011로 바꾼다
  - 그리고 점 아래 있는 애들만 잘라서 저장한다.
  - 그리고 1.0010011 * 2**3



- excess표현법

![image-20220323141337569](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220323141337569.png)

![image-20220323141350613](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220323141350613.png)



실수 자료형의 유효자릿수

32비트 (십진수) => 6자리수

64비트 (십진수) => 15자리수





파이썬

![image-20220323142805521](floating point.assets/image-20220323142805521.png)



