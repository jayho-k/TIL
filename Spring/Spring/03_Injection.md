# 03_injection

> 주입 방법
>
> - 필드 주입
>
> - 생성자 주입(Constructor Injection)
> - 세터 주입 (Setter Injection)
>
> 순환 참조방지



## 01_의존성 주입 방법

#### 1. 생성자 주입 : constructor injection

```java
@Service
public class UserService {

    private UserRepository userRepository;
    private MemberService memberService;

    @Autowired // 생성자가 하나일때 생략가능하다.
    public UserService(UserRepository userRepository, MemberService 			
                       memberService) 
    {
        this.userRepository = userRepository;
        this.memberService = memberService;
    }
    
}
```

- 생성자의 호출 시점에서 1회 호출 되는 것이 보장된다.
  - 주입받은 객체가 변하지 않거나, 반드시 객체의 주입이 필요한 경우에 강제하기 위해 사용
- @Autowired를 생략해도 주입이 가능



#### 2. 수정자 주입(Setter 주입)

```java
@Service
public class UserService {

    private UserRepository userRepository;
    private MemberService memberService;

    @Autowired
    public void setUserRepository(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Autowired
    public void setMemberService(MemberService memberService) {
        this.memberService = memberService;
    }
}
```

- 주입받는 객체가 변경될 가능성이 있는 경우에 사용
  - 변경되는 일이 극히 들물다



#### 3. 필드 주입

```java
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;
    @Autowired
    private MemberService memberService;

}
```

- 외부에서 접근이 불가능하다는 단점이 존재
- 테스트 코드의 중요성이 부각됨에 따라 필드의 객체를 수정할 수 없는 필드 주입은 거의 사용되지 않게 되었다.





## 02_생성자 주입을 사용하는 이유

> 1. 객체의 불변성 확보
> 2. final 키워드 작성 및 Lombok과의 결합
> 3. 순환 참조 에러방지



#### 1. 객체의 불변성 확보

- 의존 관계의 변경이 필요한 상황은 거의 없다
- 생성자 주입을 통해 변경의 가능성을 배제하고 불변성을 보장하는 것이 좋음



#### 2. final 키워드 작성 및 Lombok과의 결합

- 필드 객체에 final 키워드를 사용할 수 있다.
  - 컴파일 시점에 누락된 의존성을 확인할 수 있다.
  - 반면 다른 주입 방법들은 객체의 생성 이후에 호출되기 때문에 final키워드를 사용할 수 없다.
- ArgConstructor Lombok과 결합하여 사용할 수 있다.

```java
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final MemberService memberService;

    public void register(String name) {
        userRepository.add(name);
    }

}
```



#### 3. 순환 참조 에러 방지

```java
@Service
public class UserService {
	
    //UserService가 MemberService에 의존
    @Autowired
    private MemberService memberService;
    
    @Override
    public void register(String name) {
        memberService.add(name);
    }

}
```

```java
@Service
public class MemberService {

    // MemberService역시 UserService에 의존
    @Autowired
    private UserService userService;

    public void add(String name){
        userService.register(name);
    }

}
```

- UserService가 이미 MemberService에 의존하고 있는데, MemberService역시 UserService에 의존한다면 => 순환참조

- 스프링 부트 2.6부터는 이렇게 되도 에러를 발생시킨다.
- 따라서 이것은 장점이 될 수 없다.





























