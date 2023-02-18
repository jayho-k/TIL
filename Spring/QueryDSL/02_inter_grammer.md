# 02_inter_grammer



## 프로젝션과 결과 반환-기본

프로젝션 : select 대상 지정

**프로젝션 대상이 하나 일때**

```sql
List<String> result = queryFactory
         .select(member.username)
         .from(member)
         .fetch();
// 이때는 select문에 있는 member.username에 타입을 맞추면 된다.
```

- 하나 => select에 있는거 타입으로 지정하면 됨
- 둘 이상 => 불가능
  - **튜플 or DTO로 조회**



**튜플 조회**

```sql
List<Tuple> result = queryFactory
         .select(member.username, member.age)
         .from(member)
         .fetch();

for (Tuple tuple : result) {
     String username = tuple.get(member.username);
     Integer age = tuple.get(member.age);
}
# 위와 같이 .get(member.username)으로 뽑아오면 된다.
```

- 튜플을 사용할 경우 QueryDSL을 사용한다는 것을 알게된다.
  - 따라서 tuple은 repository안에서만 사용하는 것을 권장한다.
  - 나갈때는 DTO로 변환해서 나가는 것을 권장



### 프로잭션과 결과 반환 DTO로 조회

**순수 JPA에서 DTO조회**

```java
@Test
public void findDtoByJPQL(){
    List<MemberDto> result = em.createQuery(
        "select new jpa.practice2.jpa2.dto.MemberDto(m.username,m.age)" +
        " from MemberQuery m"
        ,Memb erDto.class)
        .getResultList();

    for (MemberDto memberDto : result) {
        System.out.println("memberDTO : "+ memberDto);
    }
}
```

- 너무 길다
- 오타도 자주 일어나서 쓰기가 매우 힘듦



**Querydsl 빈 생성**

> - 프로퍼티 접근
> - 필드 직접 접근 
> - 생성자 사용

**프로퍼티 접근 - setter**

```sql
    @Test
    public void findDtoBySetter(){

        List<MemberDto> result = queryFactory
                .select(Projections.bean(MemberDto.class, # 확인할 부분
                        memberQuery.username,
                        memberQuery.age))
                .from(memberQuery)
                .fetch();
        for (MemberDto memberDto : result) {
            System.out.println("MemberDto : "+memberDto);
        }
    }
```

-         queryDsl이 dto를 먼저 만들고 값을 setting 해주게 된다
-         따라서 Dto에 기본 생성자가 존재해야함



**필드접근 - field**

```sql
    @Test
    public void findDtoByField(){

        List<MemberDto> result = queryFactory
                .select(Projections.fields(MemberDto.class, # 확인할 부분
                        memberQuery.username,
                        memberQuery.age))
                .from(memberQuery)
                .fetch();
        for (MemberDto memberDto : result) {
            System.out.println("MemberDto : "+memberDto);
        }
    }

```

-         fields는 기본 생성자가 없어도 작동한다.
-         왜냐하면 필드에다가 값을 바로 집어 넣기 때문이다.



**생성자 접근 - Constructor**

```sql
    @Test
    public void findDtoByConstructor(){

        List<MemberDto> result = queryFactory
                .select(Projections.constructor(MemberDto.class, # 확인할 부분
                        memberQuery.username,
                        memberQuery.age))
                .from(memberQuery)
                .fetch();
        for (MemberDto memberDto : result) {
            System.out.println("MemberDto : "+memberDto);
        }
    }
```

- username이랑 age가 dto의 타입과 같아야한다.



**+추가** : 만약 **변수명이 안맞을 때**가 존재?

- 변수명이 안맞을 시에  matching이 안되기 때문에 null값으로 들어가게된다.
- . as({맞출 이름}) 이렇게 써서 해결하면 된다.

```sql
@Test
public void findDtoByConstructor(){

    List<MemberDto> result = queryFactory
        .select(Projections.constructor(MemberDto.class,
                                        memberQuery.username.as("name"), # 확인할 부분
                                        memberQuery.age))
        .from(memberQuery)
        .fetch();
    for (MemberDto memberDto : result) {
        System.out.println("MemberDto : "+memberDto);
    }
}
```

- 값이 없는 것을 뽑아오고 싶을때는 어떻게 해야할까?
  - ex_ member에서 max age를 가진 나이를 뽑고 싶다면 => sun query를 사용해야한다.

```sql
List<UserDto> fetch = queryFactory
     .select(Projections.fields(UserDto.class,
         	 member.username.as("name"),
             
			ExpressionUtils.as( # 없는 값이기 때문에 ExpressionUtill사용
                 JPAExpressions # JPA사용
                     .select(memberSub.age.max() # 역기서 sub쿼리를 사용하여 뽑아온다.
                  )
                 .from(memberSub), "age") # 별칭은 여기서 주게 된다.
 				))
                 .from(member)
                 .fetch();
```



## 프로제션과 결과 반환 - @QueryProjection

> 제일 깔끔하지만 단점을 가지고 있다.

**생성자 + @QueryProjection**

```java
package study.querydsl.dto;
import com.querydsl.core.annotations.QueryProjection;
import lombok.Data;
@Data
public class MemberDto {
     private String username;
     private int age;

     @QueryProjection // 이렇게 DTO생성자에 이걸 적으면 된다.
     public MemberDto(String username, int age) {
     this.username = username;
     this.age = age;
     }
}

// 사용법
@Test
public void findDtoByQueryProjection(){
    List<MemberDto> result = queryFactory
        .select(new QMemberDto(memberQuery.username, memberQuery.age))
        .from(memberQuery)
        .fetch();
}
```

- 저렇게 하면 compileQueryDsl 클릭해준다.
- 그러면 DTO도 QMemberDto로 생성해준다.

**여기서 문제점**

- Q파일을 생성해야한다는 점
- 이렇게 되면 **DTO**는 QueryDsl에 **의존성을 가지게 된다.**
  - 따라서 => **DTO를 깔끔하게 가져가고 싶을때**는 사용하지 않는다.