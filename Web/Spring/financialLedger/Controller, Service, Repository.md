# Controller, Service, Repository



DDD에서 영향을 받았다.

@Controller

- 클라이언트 요청이 오면 @Controller라고 명시된 클래스들을 탐색하는 역할을 한다.
- Mapping 주소가 일치하는 메소드를 실행시킨다.
- @RestController => JSON으로 반환



@Service

- 비즈니스 로직이 있으며 저장소 계층을 사용한다.
- 이외에 별다른 특징 사항은 없다
- 즉 @Component와 기능상 별차이가 없음



@Repository

- DB에 관련된 예외를 변환해서 던지는 기능이 있음

