# HTTPEnitty

- HttpEntity 라는 클래스가 존재
- HTTP 요청, 응답에 해당하는 HttpHeader와 HttpBody를 포함하는 클래스이다.
- 여기서 HttpEntity를 상속받아 구현한 클래스가 RequestEntity와  ResponsEntity이다.
- 즉 Http 통신을 할때 format을 Class로 구현해 놓은 Entity 라고 이해하면 된다.



## @RequestBody 와 @RequestBody의 차이점

- @RequestBody
  - 요청 내용을 자바 객체형태로 매핑된 메소드 파라미터로 전달해준다.
- @RequestBody
  - 자바 객체를 HTTP요청의 바디 내용으로 매칭하여 클라이언트로 전송해준다.
  - HTTP요청의 미디어타입과 파라미터의 타입을 먼저 확인한다.
- @RestController
  - @Controller
  - @ResponseBody
  - 이렇게 두개의 어노테이션이 포함되어있다. 따라서 RestController를 사용하게 되면 두개의 기능을 동시에 사용할 수 있음

