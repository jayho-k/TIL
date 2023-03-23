# 07_bean_lifecycle



## 빈 생명주기 콜백

- 데이터베이스 connection pool이나, network socket처럼 어플리케이션 시작 시점에 필요한 연결을 미리 해두고 종료시점에 연결을 모두 종료하는 작업을 진행하려면, **객체의 초기화와 종료작업이 필요**하다.



**조건**

이 NetworkClient 는 **애플리케이션 시작 시점에 connect() 를 호출**해서 연결을 맺어두어야 하고, **애플리케이션이 종료되면 disConnect()** 를 호출해서 연결을 끊어야 한다

```java
public class NetworkClient {
    private String url;
    
    public NetworkClient() {
        System.out.println("생성자 호출, url = " + url);
        connect();
        call("초기화 연결 메시지");
    }
    
    public void setUrl(String url){
        this.url = url
    }
    
    public void connect(){
        System.out.println("connect: " + url);
    }
    
    public void call(String message) {
        System.out.println("call: " + url + " message = " + message);
    }
    
    //서비스 종료시 호출
    public void disconnect() {
        System.out.println("close: " + url);
    }
}

```



test

```java
public class BeanLifeCycleTest {
    
    @Test
    public void lifeCycleTest(){
        // 부모는 자식을 담을 수 있음
        ConfigurableApplicationContext ac = new
            AnnotationConfigApplicationContext(LifeCycleConfig.class);
        NetworkClient client = ac.getBean(NetworkClient.class);
        ac.close();
    }
    
    @Configuration
    static class LifeCycleConfig {
        
        @Bean
        public NetworkClient networkClient() {
            NetworkClient networkClient = new NetworkClient();
            networkClient.setUrl("http://hello-spring.dev");
            return networkClient;
        }
    }
}
```

- 이렇게 진행할 경우

```
생성자 호출, url = null
connect: null
call: null message = 초기화 연결 메시지
```

이런 결과가 나오게 된다.



**이런 결과가 나오는 이유?**

- 객체를 생성하는 단계에서 url이 없고, 객체를 생성한 다음에 외부에서 수정자 주입을 통해 setUrl()이 호출 존재하게 된다.

**라이프 사이클**

- **객체 생성** => **의존관계 주입**
  - 즉 스프링 빈은 객체를 생성 => 의존관계 주입 완료 => 필요한 데이터를 사용할 준비 완료
  - 따라서 초기화 작업 = **의존관계 주입이 모두 완료 후 호출해야함**

- **순서**

  1. 스프링 컨테이너 생성

  2. 스프링 빈 생성 

  3. 의존관계 주입 

  4. 초기화 콜백 사용

  5. 소멸전 콜백 

  6. 스프링 종료



**객체의 생성과 초기화는 분리되어야 함**

- 생성자는 필수 정보(파라미터)를 받고, **메모리를 할당해서 객체를 생성하는 책임**을 가진다
- 초기화는 이렇게 **생성된 값들을 활용해서 외부 커넥션을 연결하는 등 무거운 동작**을 수행한다.
- 객체를 생성하는 부분과 초기화 하는 부분을 명확하게 나누는 것이 유지보수 관점에서 좋다고 한다.



## call back 지원

> - Interface : InitalizingBean, DisposableBean
> - 설정 정보에 초기화 메서드, 종료 메서드 지정
> - @PostContrict, @PreDestory 어노테이션

### Interface : InitalizingBean, DisposableBean

```java
public class NetworkClient implements InitializingBean, DisposableBean{
	// implements로 InitializingBean, DisposableBean 추가
    
    // ...
    
    @Override
    public void afterPropertiesSet() throws Exception {
        connect();
        call("초기화 연결 메시지");
    }
    
    @Override
    public void destroy() throws Exception {
        disConnect();
    }
    
    
}
```

- 이렇게 해주면 afterPropertiesSet에서 **의존관계 주입이 다 완료가 된 후**에 connect메소드가 나가게 된다.
- destroy() 을 사용하게 되면 **연결을 끊기 직전에 호출**

```java
// 결과
생성자 호출, url = null

NetworkClient.afterPropertiesSet
connect: http://hello-spring.dev
call: http://hello-spring.dev message = 초기화 연결 메시지

13:24:49.043 [main] DEBUG 
org.springframework.context.annotation.AnnotationConfigApplicationContext - 
Closing NetworkClient.destroy
close + http://hello-spring.dev
```

단점

- 스프링 전용 인터페이스이다.
- 지금은 사용을 많이 하지 않는다.
- 외부 라이브러리에 적용할 수 없다.



### 빈 등록 초기화, 소멸 메서드 지정

@Bean(initMethod = "init", destroyMethod = "close")

사용

```java
public class NetworkClient {
    private String url;
	// ...
    
    // ... 위와 동일한 코드
    
    public void init() {
        System.out.println("NetworkClient.init");
        connect();
        call("초기화 연결 메시지");
    }
    public void close() {
        System.out.println("NetworkClient.close");
        disConnect();
    }
}
```

```java
@Configuration
static class LifeCycleConfig {
    
    @Bean(initMethod = "init", destroyMethod = "close") // 확인할 부분
    public NetworkClient networkClient() {
        NetworkClient networkClient = new NetworkClient();
        networkClient.setUrl("http://hello-spring.dev");
        return networkClient;
    }
}
```

- 특징
  - 메서드 이름을 자유롭게 줄 수 있다.
  - 스프링 빈이 스프링 코드에 의존x
  - **코드를 고칠 수 없는 외부 라이브러리에도 초기화, 종료 메서드를 적용할 수 있다.**

-  **종료 메서드 추론**

  - **@Bean의 destroyMethod속성에서 특별한 기능**

  - 라이브러리 대부분 close, shutdown이다 => 자동으로 호출

  - `destroyMethod="" `을 사용하면 추론기능을 사용안한다는 뜻

    

### 애노테이션 @PostConstruct, @PreDestroy

```java
public class NetworkClient {
    private String url;
	/*
	 동일 코드
	*/
    
    @PostConstruct // 달라지 부분
    public void init() {
        System.out.println("NetworkClient.init");
        connect();
        call("초기화 연결 메시지");
    }
    @PreDestroy // 달라지 부분
    public void close() {
        System.out.println("NetworkClient.close");
        disConnect();
    }
}
```

```java
@Configuration
static class LifeCycleConfig {
 
    @Bean
    public NetworkClient networkClient() {
        NetworkClient networkClient = new NetworkClient();
        networkClient.setUrl("http://hello-spring.dev");
        return networkClient;
    }
}
```

- 특징

  - 자바 표준이다. 따라서 스프링이 아닌 다른 컨테이너에서도 동작

  - 컴포넌트 스캔과 잘 어울린다.

    

- **단점**

  - **외부라이브러리에는 적용할 수 없음**
  - 종료해야한다면 @Bean의 기능을 사용
    - initMethod , destroyMethod



