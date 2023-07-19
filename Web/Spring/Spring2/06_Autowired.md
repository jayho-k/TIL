# 06_Autowired



## 다양한 의존 관계 주입

### 생성자 주입

```java
@Component
public class OrderServiceImpl implements OrderService {
    private final MemberRepository memberRepository;
    private final DiscountPolicy discountPolicy;
    @Autowired
    public OrderServiceImpl(MemberRepository memberRepository, DiscountPolicy 
                            discountPolicy) {
        this.memberRepository = memberRepository;
        this.discountPolicy = discountPolicy;
    }
}
```

- 생성자 호출 시점에 딱 1번만 호출되는 것이 보장
- **불변, 필수** 의존관계에 사용
- **생성자가 1개만 있으면 @Autowired를 생략해도 자동 주입된다.**
- 빈을 등록할떄 의존관계 주입이 같이 발생
  - 왜냐하면 빈을 등록하려면 생성자가 있어야하기 때문
- private final
  - **무조건 값이 존재해야한다.**
  - 값이 없으면 에러가 뜬다.



### setter 주입

```java
@Component
public class OrderServiceImpl implements OrderService {
    private MemberRepository memberRepository;
    private DiscountPolicy discountPolicy;
    
    @Autowired
    public void setMemberRepository(MemberRepository memberRepository) {
        this.memberRepository = memberRepository;
    }
    
    @Autowired
    public void setDiscountPolicy(DiscountPolicy discountPolicy) {
        this.discountPolicy = discountPolicy;
    }
}
```

- 특징
  - **선택, 변경** 가능성이 있는 의존관계에 사용
  - 자바 빈 프로퍼티 규약의 수정자 메서드 방식을 사용하는 방법
  - setter는 빈이 먼저 등록된 후에 의존관계 주입이 일어난다.
  - 주입할 대상이 없어도 동작하게 하려면 @Autowired(required = false) 로 지정하면 된다

- 자바빈 프로퍼티

```java
class Data {
    private int age;
    
    public void setAge(int age) {
        this.age = age;
    }
    
    public int getAge() {
        return age;
    }
}
```



### 필드 주입

```java
@Component
public class OrderServiceImpl implements OrderService {
    @Autowired
    private MemberRepository memberRepository;
    
    @Autowired
    private DiscountPolicy discountPolicy;
}
```

- 외부에서 변경이 불가능해서 테스트 하기 힘들다는 치명적인 단점이 있다
- DI 프레임워크가 없으면 아무것도 할 수 없다. 
- 사용하지 말자!
  - 애플리케이션의 실제 코드와 관계 없는 테스트 코드 
  - 스프링 설정을 목적으로 하는 @Configuration 같은 곳에서만 특별한 용도로 사용



일반 메서드 주입

```java
@Component
public class OrderServiceImpl implements OrderService {
    private MemberRepository memberRepository;
    private DiscountPolicy discountPolicy;
    
    @Autowired
    public void init(MemberRepository memberRepository, DiscountPolicy 
                     discountPolicy) {
        this.memberRepository = memberRepository;
        this.discountPolicy = discountPolicy;
    }
}
```

- 아무 메서드에다가 Autowired를 할 수 있음
- 사용할 일 거의 없음



### 옵션 처리

- 자동주입 대상
  - `@Autowired(required=false)` : 자동주입할 대상이 없으면 수정자 메서드 호출 안됨
  - `org.springframework.lang.@Nullable` : 자동 주입할 대상이 없으면 null이 입력
  - `Optional<>` 자동 주입할 대상이 없으면 Optional.empty가 입력



### 생성자 주입을 선택해야하는 이유

**불변**

- 대부분의 의존관계 주입은 한번 일어나면 애플리케이션 종료시점까지 의존관계를 변경할 일이 없다. 애플리케이션 종료 전까지 변하면 안된다.(불변해야 한다.)
- 수정자 주입을 사용하면, setXxx 메서드를 public으로 열어두어야 한다.
  - 누군가 실수로 변경할 수 도 있고, 변경하면 안되는 메서드를 열어두는 것은 좋은 설계 방법이 아니다

**누락**

- setter 주입을 사용할 경우 단위 테스트를 할때 에러가 발생
  - memberRepository,  discountPolicy 모두 의존관계 주입이 누락되었기 때문이다
- 하지만 생성자 주입같은 경우에는 주입 데이터를 누락했을 때 **컴파일 오류가 발생**
  - 따라서 **어떤 값을 필수로 주입해야하는지 알수 있음**



**final을 넣을 수 있음**	

- 생성자에서 혹시 값이 설정되지 않는 오류를 컴파일 시점에서 막아준다.
  - 값이 무조건 있어야 하는데 없기 때문이다
- 생성자 주입방식은 생성자 호출될 때 같이 되기 때문에 final 키워드를 유일하게 사용할 수 있음

```java
@Component
public class OrderServiceImpl implements OrderService {
    
    private final MemberRepository memberRepository;
    private final DiscountPolicy discountPolicy; // 

    @Autowired
    public OrderServiceImpl(MemberRepository memberRepository, DiscountPolicy 
                            discountPolicy) {
        this.memberRepository = memberRepository;
        // discountPolicy가 빠져있음
    }
    //...
}
```

- discountPolicy가 위와 같이 빠져있을 경우에 컴파일 에러가 난다.

  



## 롬복과 최신 트랜드

- 생성자 주입을 사용해야한다.
  - 하지만 귀찮다, 생성자도 만들어야하고 주입받는 값을 대입해야하기 때문

```java
@Component
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {
    private final MemberRepository memberRepository;
    private final DiscountPolicy discountPolicy;
}
```

- @RequiredArgsConstructor 사용
  - 생성자 코드를 그대로 만들어준다.



## @Qualifier, @Primary

### 조회 빈 2개 이상 일경우

- @Autowired는 Type으로 조회하게 된다. 
- DiscountPlolicy의 하위 타입
  - FixDiscountPolicy
  - RateDiscountPolicy
  - **=> 이것을 둘다 스프링 빈으로 선언한다면?? => 충돌**
  - 둘다 사용하고 싶을 경우 어떻게 해야할까?



### @Qualifier, @Primary 사용

> - @Autowired 필드 명 매칭 
> - @Qualifier => @Qualifier끼리 매칭 => 빈 이름 매칭
> -  @Primary 사용

**@Autowired 필드 명 매칭** 

1. 타입 매칭
2. 타입 매칭의 결과가 2개 이상일 때 필드 명, 파라미터 명으로 빈 이름 매칭



**@Qualifier 사용**

- 추가 구분자를 붙여주는 방법

```java
@Component
@Qualifier("mainDiscountPolicy")
public class RateDiscountPolicy implements DiscountPolicy {}

@Component
@Qualifier("fixDiscountPolicy")
public class FixDiscountPolicy implements DiscountPolicy {}
```

- 이런식으로 주입시에 등록한 이름을 적어준다.



```java
@Autowired
public OrderServiceImpl(MemberRepository memberRepository,
                        @Qualifier("mainDiscountPolicy") DiscountPolicy 
                        discountPolicy) {
    this.memberRepository = memberRepository;
    this.discountPolicy = discountPolicy;
}
```

- 이렇게 별칭같은 것을 부여한다음에 그것을 사용하는 것이다.

순서

1. @Qualifier끼리 매칭
2. 빈 이름 매칭
3. NoSuchBeanDefinitionException 예외 발생



**@Primary 사용**

- 우선순위를 정하는 방법
- @Autowired 시에 여러 빈이 매칭되면 @Primary 가 우선권을 가진다.

```java
@Component
@Primary
public class RateDiscountPolicy implements DiscountPolicy {}

@Component
public class FixDiscountPolicy implements DiscountPolicy {}
```

- rateDiscountPolicy 가 우선권을 가지게 된다.



**우선순위**

- @Qualifier가 우선순위가 더 높음



## 애노테이션 직접 만들기

```java
// 타겟을 정해주는 것
@Target({ElementType.FIELD, ElementType.METHOD, ElementType.PARAMETER,
         ElementType.TYPE, ElementType.ANNOTATION_TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Qualifier("mainDiscountPolicy")
public @interface MainDiscountPolicy {} // 이렇게 @를 붙혀서 annotation을 만듦
```

```java
//RateDiscountPolicy
@Component
@MainDiscountPolicy // 여기에 위에서 만든 annotation을 추가한 것, 즉 
				  // 즉 @Qualifier(" ") => 이것을 annotation형태로 만든 것이다.
public class RateDiscountPolicy implements DiscountPolicy {}
```

```java
@Autowired
public DiscountPolicy setDiscountPolicy(
		@MainDiscountPolicy DiscountPolicy discountPolicy) {
    	// @Qulifier가 있던 자리를 @MainDiscountPolicy로 넣어준 것
    this.discountPolicy = discountPolicy;
}
```



## 조회한 빈이 모두 필요할 때, List, Map 

- List나 Map으로 모두 가져올 수 있다.
  - 즉 interface로 DiscountPolicy가 되어 있는 것 
    - 하지만 Implements로 Rate와 Fix둘다 있을 경우 이때 모두 조회한다는 뜻

- 이렇게 하면 동적으로 편하게 처리할 수 있을때가 있기 때문이다.

```java
@Test
void findAllBean() {
    ApplicationContext ac = 
        new AnnotationConfigApplicationContext(AutoAppConfig.class, 		
											DiscountService.class);
    
    DiscountService discountService = ac.getBean(DiscountService.class);
    
    Member member = new Member(1L, "userA", Grade.VIP);
    int discountPrice = discountService.discount(member, 10000,
                                                 "fixDiscountPolicy");
    assertThat(discountService).isInstanceOf(DiscountService.class);
    assertThat(discountPrice).isEqualTo(1000);
}

static class DiscountService {
    // Map으로 
    private final Map<String, DiscountPolicy> policyMap;
    
    // List로
    private final List<DiscountPolicy> policies;

    // 생성자
    public DiscountService(Map<String, DiscountPolicy> policyMap,
                           List<DiscountPolicy> policies) {
        this.policyMap = policyMap;
        this.policies = policies;
    }
    
    // 
    public int discount(Member member, int price, String discountCode) {
        DiscountPolicy discountPolicy = policyMap.get(discountCode);
        return discountPolicy.discount(member, price);
    }
 
```



## 실무

> - 정리 편리한 자동 기능을 기본으로 사용
> - 직접 등록하는 기술 지원 객체는 수동 등록 
> - 다형성을 적극 활용하는 비즈니스 로직은 수동 등록을 고민

**편리한 자동 기능을 기본으로 사용**

**수동 빈 등록은 언제?**

- **업무 로직 빈**
  - 웹을 지원하는 컨트롤러, 핵심 비즈니스 로직이 있는 서비스, 데이터 계층의 로직을 처리하는 리포지토리등이 모두 업무 로직이다. 보통 비즈니스 요구사항을 개발할 때 추가되거나 변경된다.
  - **자동 기능 사용**



- **기술 지원 빈**
  - 기술적인 문제나 공통 관심사(AOP)를 처리할 때 주로 사용된다. **데이터베이스 연결**이나,  **공통 로그 처리** 처럼 업무 로직을 지원하기 위한 **하부 기술이나 공통 기술들**이다.
  - **수동 빈 사용**
    - 빈 수가 적음
    - 기술지원 도맂ㄱ은 적용이 잘 되는지 파악하기 힘든 경우가 많음
    - 따라서 수동 빈으로 등록해서 사용하는 것이 명확하게 들어나서 좋음
  - 애플리케이션에 광범위하게 영향을 미치는 기술 지원 객체는 수동 빈으로 등록해서 딱! 설정 정보에 바로 나타나게 하는 것이 유지보수 하기 좋다



- **비즈니스 로직 중에서 다형성을 적극 활용할 때** => 수동 빈 사용

  - DiscountService은 하위 빈들이 있음

  - 따라서 수동빈으로 만들어 놓으면 **한 눈에 어떤 빈들이 있는지 파악하기가 쉬움**

  - ```java
    @Configuration
    public class DiscountPolicyConfig {
    
        @Bean
        public DiscountPolicy rateDiscountPolicy() {
            return new RateDiscountPolicy();
        }
        @Bean
        public DiscountPolicy fixDiscountPolicy() {
            return new FixDiscountPolicy();
        }
    }
    ```







