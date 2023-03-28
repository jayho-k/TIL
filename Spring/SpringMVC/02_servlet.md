# 02_servlet

```
@WebServlet(name = "helloServlet", urlPatterns = "/hello")
```

- 

<img src="./02_servlet.assets/image-20230328024100950.png" alt="image-20230328024100950" style="zoom:67%;" />

- 스프링 부트 실행 => 스프링 부트가 **내장 톰켓서버 실행**
- 톰켓 서버는 내부에 서블릿 컨데이터를 가지고 있음
  - 서블릿을 생성

<img src="./02_servlet.assets/image-20230328024248977.png" alt="image-20230328024248977" style="zoom:67%;" />

<img src="./02_servlet.assets/image-20230328024309937.png" alt="image-20230328024309937" style="zoom:80%;" />

- HTTP 요청 메시지를 기반으로 request, response객체를 만든다
- singleton으로 떠있는 서블릿을 호출한다.
- response로 Http응답으로 만들어서 반환을 해준다.





















