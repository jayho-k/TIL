# Interface와 Abstract 차이

- **공통점**

  - 상속받는 클래스 혹은 구현하는 인터페이스 안에 있는 추상 메소드를 구현하도록 강제 하는 것
    

- **차이점**

  - 추상클래스

    - 추상 클래스내 추상 메소드가 하나 이상 포함되거나 abstract로 정의된 경우

    - 목적 : 추상클래스를 상속 받아서 기능을 이용하고 확장시키는데 있다

      - 즉 기능을 이용하거나 확장하기 위해서 사용

    - ```java
      abstract class Predator extends Animal {
          abstract String getFood();
      
          void printFood() {
              System.out.printf("my food is %s\n", getFood());
          }
      }
      ```

    

  - 인터페이스

    - 모든 메소드가 추상메소드인 경우
    - 함수의 껍데기만 있다.
    - 구현한 객체들에 대해서 동일한 동작을 약속하기 위해서 존재









