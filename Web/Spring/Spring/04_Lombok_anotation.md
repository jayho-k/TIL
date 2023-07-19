# 04_Lombok_anotation

출처

https://www.daleseo.com/lombok-popular-annotations/

## 접근자/설정자 자동 생성

```java
@Getter 
@Setter
private String name;
```

```java
user.setName("홍길동");
String userName = user.getName();
```

- 위와 같이 사용이 가능하다
- 필드 레벨이 아닌 클래스 레벨에 `@Getter` 또는 `@Setter`를 선언해줄 경우, 모든 필드에 접근자와 설정자가 자동으로 생성



## 02_생성자 자동 생성

`@NoArgsConstructor`

- 파라미터가 없는 **기본 생성자**를 생성



`@AllArgsConstructor`

- **모든 필드 값**을 파라미터로 받는 생성자 생성



`@RequiredArgsConstructor`

- final이나 `@NonNull`인 필드 값만 파라미터로 받는 생성자를 생성



```java
@NoArgsConstructor
@RequiredArgsConstructor
@AllArgsConstructor
public class User {
  private Long id;
  @NonNull
  private String username;
  @NonNull
  private String password;
  private int[] scores;
}
```

```java
//@NoArgsConstructor : 기본 생성자
User user1 = new User();

//@RequiredArgsConstructor : null이 아니면 안되는 것들을 필수적으로 넣어줘야함
User user2 = new User("dale", "1234"); 

// @AllArgsConstructor : 모두 넣어줘야함, 아닐 경우 null값을 넣어줘야 한다.
User user3 = new User(1L, "dale", "1234", null);
```



## 03_ToString

```java
@ToString(exclude = "password")
public class User {
  private Long id;
  private String username;
  private String password;
  private int[] scores;
}
```

```java
User user = new User();
user.setId(1L);
user.setUsername("dale");
user.setUsername("1234");
user.setScores(new int[]{80, 70, 100});
System.out.println(user);
```

- 위와 같이 사용하게 되면

```java
User(id=1, username=1234, scores=[80, 70, 100])
```

- 이러한 결과를 얻을 수 있다.



## 04_@Builder

- 해당 객체의 생성에 Bulder패턴을 적용시켜준다.
- 모든 변수에 대해 buld하기를 원한다면 클래스 위에 @Builder를 붙이면 되지만, 특정 변수만을 build하기 원한다면 생성자를 작성하고 그 위에 @Builder어노테이션을 붙여 준다.
- 쓰는 이유
  - 가독성
  - 순서 상관 없음
  - 

```java
@Getter
@NoArgsConstructor
public class Store extends Common {

    private String companyName;                                 // 상호명
    private String industryTypeCode;                            // 업종코드
    private String businessCodeName;                            // 업태명
    private String industryName;                                // 업종명(종목명)
    private String telephone;                                   // 전화번호
    private String regionMoneyName;                             // 사용가능한 지역화폐 명
    private boolean isBmoneyPossible;                           // 지류형 지역화폐 사용가능 여부
    private boolean isCardPossible;                             // 카드형 지역화폐 사용가능 여부
    private boolean isMobilePossible;                           // 모바일형 지역화폐 사용가능 여부
    private String lotnoAddr;                                   // 소재지 지번주소
    private String roadAddr;                                    // 소재지 도로명주소
    private String zipCode;                                     // 우편번호
    private double longitude;                                   // 경도
    private double latitude;                                    // 위도
    private String sigunCode;                                   // 시군 코드
    private String sigunName;                                   // 시군 이름

    @Builder
    public Store(String companyName, String industryTypeCode){
        this.companyName = companyName;
        this.industryTypeCode = industryTypeCode;
    }
    
}
```

```java
@RestController
@RequestMapping(value = "/store")
@Log4j2
public class StoreController {

    @GetMapping(value = "/init")
    private ResponseEntity init(){
        Store store = Store.builder()
                .companyName("회사이름")
                .industryTypeCode("업종코드")
                .build();

        return ResponseEntity.ok(store);
    }

}
```







## 05_equals, hashCode 자동 생성

equals :  2개의 객체가 동일한지 검사하기 위해 사용

hashCode : 실행 중에(Runtime) 객체의 유일한 integer값을 반환한다.
					 Object 클래스에서는 heap에 저장된 객체의 메모리 주소를 반환하도록 되어있다. 



```
@EqualsAndHashCode(callSuper = true)
public class User extends Domain {
  private String username;
  private String password;
}
```

`callSuper` 속성을 통해 `equals`와 `hashCode` 메소드 자동 생성 시 부모 클래스의 필드까지 감안할지 안 할지에 대해서 설정할 수 있음

즉, `callSuper = true`로 설정하면 부모 클래스 필드 값들도 동일한지 체크하며, `callSuper = false`로 설정(기본값)하면 자신 클래스의 필드 값들만 고려한다.











