# @Autowired와 static final 차이



### private final => [가장 선호]

- 생성자 주입 : Constrictor Injection

### @Autowired

- 필드 주입 : Field Injection
  - 필드에 자동으로 의존성 주입

### Setter

- 수정자 주입 : Setter  Injection

- **@Autowired와 setter는 필드를 final로 선언할 수 없음**



## 생성자 주입이 선호되는 이유

> - 순환 참조 방지
> - 테스트 용이
> - final 선언 가능 => 불변성 보장

### 1. 순환 참조 방지

- 필드 주입과 수정자 주입은 먼저 빈을 생성한 뒤, 주입하려는 빈을 찾아 주입한다.
- 생성자 주입은 먼저 빈을 생성하지 않고 주입하려는 빈을 찾는다.
- 따라서 생성자 주입을 사용하면 서버 자체가 구동이 되지 않아 순환 참조가 실행되면서 방지할 수 있음 => 사전에 순환 참조 방지

### 2. 테스트 용이

- 생성자 주입은 단순히 원하는 객체를 생성하고 생성자에 넣어주면 된다.



### 3. final 선언 가능

- 필드와 수정자는 final로 선언이 불가하다.
  - 즉 언제든 변경될 수 있다는 뜻
- 생성자 주입은 final로 필드 선언이 가능하다. 따라서 런타임에 객체 불변성을 보장한다.



- 왜 필드와 수정자 주입은 final을 사용할 수 없을까?
  - 객체 생성 시점이 아닌 생성 이후에 의존성을 주입하기 때문
  - 객체 생성 이후 reflection으로 우회해서 강제로 값을 할당하기 떄문입니다.
    - reflection이란
      - 프로그램이 실행 중에 클래스의 정보를 동적으로 가져올 수 있는 기술
      - 이를 통해 클래스의 멤버 (field, method, contructor)에 접근하고 수정할 수 있음
      - 즉 Reflection은 런타임에 동적으로 클래스를 조작할 수 있는 유연성 제공
      - https://velog.io/@goseungwon/Java-Reflection



- final이란?

  - 값이 불변한 값으로 만드는 것을 뜻한다.

  - 즉 `final int num = 10;`  이라면 계속 값 10인 값을 가져야한다.
  - 메모리에 값이 올라가는 시점부터 불변을 





별첨

순환참조

- A class 가 B class의 Bean을 주입, B class가 A class의 Bean을 주입 받는 상황
- 필드 주입 방식과 수정자 주입 방식에는 위 같은 상황이 일어나도 Application 실행 과정ㅇㅇ에서 예외가 발생하지 않음
  - 즉 실제로 메소드가 호출될 때 발생
  - 즉 순환 참조 문제가 발생하는 것이 아닌 순환 호출이 발생하게 된다.

- 생성자 주입 방식의 동작 원리

  - 가정

    - A class가 B class를 의존
    - B class가 C class를 의존

  - 동작

    - A class에 대한 Bean을 만들기 위해서 B class의 Bean을 주입해야함

    - 하지만 B class의 Bean이 없어 B Bean을 생성

    - 이떄 B class에 C class의 Bean을 주입해야하는데 없음 => C class의 Bean을 가장 먼저 만들게 된다.

    - 즉 Bean만드는 순서

      - C => B => A 순으로 Bean을 생성하게 된다.

        

  - 순환 참조 가정

    - A <=> B

  - 동작

    - A class의 Bean을 만들때 B class의 Bean이 필요
    - B class의 Bean을 만들때 A class의 Bean이 필요
    - 무한 반복 => **순환참조 문제 발생**
      - 즉 서버가 실행되기 전에 이 상황에 대해 알 수 있음



























