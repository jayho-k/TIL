# ORM

https://mangkyu.tistory.com/20



- 언어 객체지향에 관하여
  - https://jongminfire.dev/%EA%B0%9D%EC%B2%B4%EC%A7%80%ED%96%A5-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D%EC%9D%B4%EB%9E%80

## 01_Object Relation Mapping?

#### 1. ORM이란?

- Object와 DB의 테이블을 Mapping시켜 RDB테이블을 `객체지향적`으로 사용하게 하는 기술
- RDB 테이블은 객체지향적 특성(상속, 다형성, 레퍼런스) 등이 없어서 Java와 같은 객체지향적 언어로 접근하는 것이 쉽지 않음
- JPA와 그의 구현체 Hibernate가 있음



> 객체지향 프로그래밍(OOP)이란?
>
> - Object-Oriented Programming
>
> - 프로그래밍에서 **필요한 데이터를 `추상화`**시켜 **상태와 행위를 가진 객체**를 만들고 그객체들간의 상호작용을 통해 로직을 구성하는 프로그래밍
> - language파트에서 자세히



#### 2. **MyBatis VS Hibernate 비교** 

- 안전성과 속도를 매우 중시할 경우 직접작성하는 Mybatis가 좋을 수 있음
- Hibernate에 능숙해진다면 생산성을 상당히 높힐 수 있음



## 02_JPA & MyBatis & X

#### ORM을 사용하지 않을 경우

```java
public void insertUser(User user){
    String query = " INSERT INTO user (email, name, pw) VALUES (?, ?, ?)";

    PreparedStatement preparedStmt = conn.prepareStatement(query);
    preparedStmt.setString (1, user.getEmail());
    preparedStmt.setString (2, user.getName());
    preparedStmt.setString (3, user.getPW());

    // execute the preparedstatement
    preparedStmt.execute();
}
```

- setString각각을 모두 set을 사용해서 Mapping을 하게 된다.
- **가독성이 떨어짐**



#### spring-data-mybatis

```java
@Mapper
@Repository
public interface UserMapper {
    insertUser(User user);
}
```

```java
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="mang.blog.user.userMapper">

    <insert id="insertUser" parameterType = "user">
        INSERT USER(
            email, name, pw, 
        )VALUES(
            #{email}, #{name}, #{pw}
        )
    </insert>

</mapper>
```

- 1번째 : Mapper interface
- 2번째 : Mapper.xml
- Repository에서 메소드의 이름은 queryId에 매핑되며 xml 파일에서 해당 쿼리의 id를 기준으로 쿼리를 실행한다.



#### JPA를 사용한 코드

**Entity**

```java
@Entity
@Table(name = "user")
@Getter
@Builder
@NoArgsConstructor(force = true)
@AllArgsConstructor
public class User extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String email;
    private String name;
    private String pw;
}
```



**Repository**

```java
public interface UserRepository extends JpaRepository <User, Long> {

}
```



**Service**

```java
@Service
@RequiredArgsConstructor
@Transactional(readonly = true)
public class UserService {

    private final UserRepository userRepository;

    @Transactional
    public User findUserAndUpdateName(Long id) {
        User user = userRepository.findById(id);
        user.setName("변경된 이름");
    }
}
```

- Update를 할 때 update쿼리를 사용하지 않음
- JPA는 DB에서 조회한 데이터들을 객체로 연결 시킴
  - 즉 객체값을 수정하는 것 = DB값을 수정하는 것
  - 해당 매소드가 종료될 때 update쿼리가 JPA의 값이 변경 유무를 감지하는 `Dirty checking` 이후에 나가게 된다.
- 이를 통해 JPA는 MyBatis와 달리 쿼리를 직접 작성하지 않음



>  Dirty checking 이란?
>
> - JPA에서는 트랜젝션이 끝나는 시점에 **변화가 있는 모든 엔티티 객체를 DB에 자동으로 반영**해준다
>
> - 변화 기준 : **최초 조회 상태**
>   1. 최초 조회 상태를 스냅샷으로 만들어 놓음
>   2. 트랜잭션이 끝남 => 스냅샷과 비교
>   3. 다른 점이 있다면 Update
> - 준영속/비영속 상태의 엔티티는 Dirty Checking대상에 포함되지 않음
>   (값을 변경해도 DB에 방영되지 않음)
>   - 준영속 : Detach(분리?)된 엔티티
>   - 비영속 : DB에 방영되기 전 처음 생성된 엔티티



## 03_JPA를 사용하는 이유

> 1. 엔티티에 맞는 테이블 생성 + DB생성 편리
>
> 2. 객체 지향 중심의 개발
> 3. 테스트 작성이 용이
> 4. 기본적인 CRUD자동화 => 생산성이 높아짐
> 5. 복잡한 쿼리는 QueryDSL을 사용해서 처리



#### 복잡한 쿼리는 QueryDSL을 사용해서 처리

- JPA를 이용하다보면 동적 쿼리를 처리하기가 매우 어려움
- QueryDSL 이라는 오픈소스를 사용한다면 문제를 해결할 수 있다.
- QueryDSL을 이용한 예시이며 자바 언어로 매우 직관적인 쿼리를 작성할 수 있다는 장점이 있다.

```java
@Repository
@RequiredArgsConstructor
public class QuizRepositoryImpl {

    private final JPAQueryFactory query;

    @Override
    public User search(final String email) {
        final QUser qUser = QUser.user;

        final User user = query.selectFrom(qUser)
                .where(qUser.email.equalsIgnoreCase(email))
                .fetch();
        return user;
    }
}
```









