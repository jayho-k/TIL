# 08_bean_scope



## 빈 스코프란?

- 빈이 존재할 수 있는 범위

- **싱글톤**
  - 기본 스코프, 스프링 컨테이너의 시작과 종료까지 유지되는 가장 넓은 범위의 스코프

- **프로토 타입**
  - 프로토 타입 빈의 생성과 의존관계 주입까지만 관여

- **웹 관련 스코프**
  - request : 웹 요청이 들어오고 나갈때 까지 유지되는 스코프
  - sesssion : 웹 세션이 생성되고 종료될때까지 유지
  - application : 웹 서블릿 컨텍스트와 같은 범위로 유지

**등록 방법**

- 컴포넌트 스캔 자동 등록

```java
@Scope("prototype")
@Component
public class HelloBean {}
```



- 수동 등록

```java
@Scope("prototype")
@Bean
PrototypeBean HelloBean() {
    return new HelloBean();
}
```



## 프로토 타입 스코프





