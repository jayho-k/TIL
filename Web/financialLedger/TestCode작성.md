# TestCode작성



## 01_ 좋은 단위 Test란

> - 출처
>   - https://dingdingmin-back-end-developer.tistory.com/entry/Springboot-Test-%EC%BD%94%EB%93%9C-%EC%9E%91%EC%84%B1-1

1. **1개의 테스트는 1개의 기능에 대해서만 테스트**
2. **테스트 주체와 협력자를 구분하기**
   - 주체 : 테스트 할 객체
   - 협력자 : 테스트를 진행하기 위해 정의하는 가짜 객체
3. **Given, when, then으로 명확하게 작성**
   - Given : 테스트를 진행할 행위를 위한 사전 준비
   - When : 테스트를 진행할 행위
   - then : 테스트를 진행한 행위에 대한 결과 검증



## 02_Test코드 예시

```java
// Member
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Getter
public class Member {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
 
    @Column(name = "name")
    private String name;
 
    @Column(name = "age")
    private int age;
 
    @Builder
    public Member(String name, int age){
        this.name=name;
        this.age=age;
    }
 
    @Override
    public boolean equals(Object obj) { // 협력자에서 이름 중복 예외를 검증하기 위함
        Member me = (Member) obj;
        return this.name.equals(me.name) && this.age==me.age;
    }
 
    public void changeAge(int age){
        this.age=age;
    }
}


//MemberRepository
public interface MemberRepository extends JpaRepository<Member,Long> {
 
    Optional<Member> findByName(String name);
}

//MemberService, MemberServiceImpl

public interface MemberService {
    List<MemberResponseDto.ListDto> findAll();
    Long createMember(String name, int age);
}

@Service
@Transactional
@RequiredArgsConstructor
public class MemberServiceImpl implements MemberService{
 
    private final MemberRepository memberRepository;
    
    @Override
    public List<MemberResponseDto.ListDto> findAll(){
        return memberRepository.findAll().stream().map(
            	a -> new MemberResponseDto.ListDto(a.getName(),a.getAge()))
                .collect(Collectors.toList());
    }
 
    @Override
    public Long createMember(String name, int age){
        memberRepository.findByName(name).ifPresent(a -> {
            throw new IllegalStateException("이미 있는 아이디");
        });
        Member member = Member.builder()
                .age(age)
                .name(name).build();
        
        return memberRepository.save(member).getId();
    }
}

// MemberController, MemberControllerAdvice
@RestController
@RequiredArgsConstructor
public class MemberController {
 
    private final MemberService memberService;
 
    @GetMapping("/members")
    public List<MemberResponseDto.ListDto> getMemberList(){
        return memberService.findAll();
    }
 
    @PostMapping("/members")
    public Long createMember(@RequestBody MemberRequestDto.CreateDto createDto){
        return memberService.createMember(createDto.getName(), createDto.getAge());
    }
}

@RestControllerAdvice(basePackages = "com.example.fortest.domain.member.controller")
public class MemberControllerAdvice {
 
    @ExceptionHandler
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public String duplicate(IllegalStateException e){
        return e.getMessage();
    }
}

// DTO
public class MemberRequestDto {
 
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CreateDto {
        String name;
        int age;
    }
}
public class MemberResponseDto {
 
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ListDto {
        String name;
        int age;
    }
}

```

















## Test코드

### AsserJ 라이브러리 기능

1. assertThat
   - 검증할 때 사용
   - assertThat(실제 값).isEqualTo(기대값)
   - assertThat(실제 값).isNull()
   - assertThat(실제 객체).isInstanceOf(객체 예산 타입) 등
     
2. assertthatThrowBy
   - 예외 발생 검증에 사용된다.
   - ex_ assertThatThrowBy(()-> 예외를 발생시킬 로직).isInstanceOf(예외 클래스)
   - 예외가 발생하면 테스트를 통과한다.



### 도메인 Test

```java

@Test
@DisplayName("test")
void createMember(){
    // given
    Member memeber = Member.builder().age(10).name("hi").build();
    // when    // then
    Assertions.assertThat(member.getAget()).isEqualTo(10);
    Assertions.assertThat(member.getName()).isEqualTo("hi");
    
}

```



### Jpa를 사용하는 Repository Test

```java
@Test
@DisplayName("멤버 생성")
void createMember(){
    Member member1 = Member.builder().name("hi1").age(10).build();
    Member member2 = Member.builder().name("hi2").age(20).build();
    
    Member result1 = memberRepository.save(member1);
    Member result2 = memberRepository.save(member2);
    
    assertThat(result1.getAge()).isEqualTo(member1.getAge());
    assertThat(result2.getAge()).isEqualTo(member2.getAge());
 
}



// assertThat(result.size()).isEqualTo(2); list생성했을때 확인

```



### Service 계층 Test

- 주체 : Service 객체
- 협력자 : Repository 객체
  - Repository는 가짜 객체로 응답해줘야함
  - **@ExtendWith(SpringExtension.class)**를 사용해야한다.

```java
@ExtendWith(SpringExtension.class)
public class MemberServiceTest {
    
    // service : 주체
    MemberService memberservice;
    
    // Repo : Test협력자
	@MockBean // 가짜 객체를 만드는 역할, 
    MemberRepository memberRepository;
    
    // Test를 실행하기 전마다 memberService에게 가짜 객체를 주입
    @BeforeEach
    void setUp(){
        memberService = new MemberServiceImpl(memberRepository)
    }
}
```



- Member 생성 성공

```java
@Test
@DisplayName("멤버 생성 성공")
void createMemberSuccess(){
	// memeber생성
    Member member3 = Member.builder().name("hi3").age(10).build();
    ReflectionTestUtils.setField(member3,"id",3l);
 
	// 가짜 객체 응답 정의    
    Mockito.when(memberRepository.save(member3)).thenReturn(member3); 
    
    //when
    Long hi3 = memberService.createMember("hi3", 10);

    // then
    assertThat(hi3).isEqualTo(3L);
}
```

- ReflectionTestUtils.setFeild : test를 진행할때 private으로 선언된 필드값을 넣어줄 수 있음
- Mockito.when(가짜 객체의 로직 실행).thenReturn(반환하는 값);



- member1과 이름이 같아서 예외발생

```java
@Test
@DisplayName("멤버 생성시 member1 과 이름이 같아서 예외 발생")
void createMemberFail(){
    
    //given
    Member member1 = Member.builder().name("hi1").age(10).build();
    Mockito.when(memberRepository.findByName("hi1"))
        								.thenReturn(Optional.of(member1));
 
    //when then
    assertThatThrownBy(() -> memberService.createMember("hi1",10))
        						.isInstanceOf(IllegalStateException.class);
}
```

- memberService.createMember("hi1",10))를 만들었을때 IllegalStateException 에러 발생
- 에러가 발생할 경우 테스트 통과



### Controller 계층

- @WebMvcTest 
  - Mvc를 위한 테스트로 컨트롤러가 설계대로 동작하는지에 대해 검증
  - Controller를 구체적으로 적을수 있으며, ControllerAdivce,Filter등을 포함, 제외 시킬 수 있다. 
  - Securiry에 대한 Test도 가능하다.



```java
@WebMvcTest(MemberController.class)
public class MemberControllerTest {
 
    @Autowired
    MockMvc mvc;
 
    @MockBean
    MemberServiceImpl memberService;
}
```

- 주체 : Controller = WebMvcTest에 선언
- 협력자 : Service = @MockBean에 등록
  - 테스트 때 생성되는 WebApplicationContext에서 주입받는다

```java
@Test
@DisplayName("리스트 반환받기")
void getList() throws Exception {

   // given
   List<MemberResponseDto.ListDto> list = List.of(
       		new MemberResponseDto.ListDto("asd", 10)
           , new MemberResponseDto.ListDto("fsd", 12));
    Mockito.when(memberService.findAll()).thenReturn(list);
 
   // when then
    mvc.perform(MockMvcRequestBuilders.get("/members")
            .contentType(MediaType.APPLICATION_JSON))
            .andDo(MockMvcResultHandlers.print())
            .andExpect(MockMvcResultMatchers.status().isOk())
            .andExpect(MockMvcResultMatchers.jsonPath("$[1].name").value("fsd"))
            .andExpect(MockMvcResultMatchers.jsonPath("$[0].name").value("asd"));
}
```

-  mvc.perform(MockMvcRequestBuilders.get("/members")
              .contentType(MediaType.APPLICATION_JSON))
  - 컨트롤러에게 요청을 보내는 역할/ uri를 만들고, contentType을 지정
- andDo : 요청에 대한 처리
  - MockMvcResultHanlder.print()를 인자로 넣으면 요청과 응담에 대한 것들을 콘솔에 출력
- andExpect() => 검증
  - MockMvcResultMatchers.status().isOk() : 상태 검증
- jsonPath("$. name"). value("fsd"): 단일 객체에 대한 값 검증
- jsonPath("$[1]. name"). value("asd): 리스트를 반환받았을 때 지정하여 검증



































