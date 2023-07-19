# 01_basic_grammer

[TOC]

- QueryDSL은 Git에서 관리하면 안된다.
- 자동으로 generate된 코드이기 때문이다.
- Build안에 generate했기 때문에 git ignore이 되어 있을 것이다.



## Setting

```java
// 스프링 부트 2.6 이상 부터는 querydsl 5.0을 사용
buildscript {
	ext {
		queryDslVersion = "5.0.0"
	}
}
plugins {
	id 'java'
	id 'org.springframework.boot' version '2.7.8'
	id 'io.spring.dependency-management' version '1.0.15.RELEASE' 
	id "com.ewerk.gradle.plugins.querydsl" version "1.0.10" // query dsl 확인부분
}

group = 'jpa.practice2'
version = '0.0.1-SNAPSHOT'
sourceCompatibility = '11'

configurations {
	compileOnly {
		extendsFrom annotationProcessor
	}
}

repositories {
	mavenCentral()
}

dependencies {
	implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
	implementation 'org.springframework.boot:spring-boot-starter-validation'
	implementation 'org.springframework.boot:spring-boot-starter-web'
	implementation 'com.fasterxml.jackson.datatype:jackson-datatype-hibernate5' //

	compileOnly 'org.projectlombok:lombok'

	// 5.0 이전 버전에는 'com.querydsl:querydsl-jpa' 의존성만 추가하면 됐지만
	// 5.0 이후 버전에는 3개의 프로젝트로 갈라진거 같다.
	// querdysl ${querydDslVersion} 은 맨위에 선언한 5.0 변수를 사용함
	//implementation 'com.querydsl:querydsl-jpa'
	implementation "com.querydsl:querydsl-jpa:${queryDslVersion}"
	implementation "com.querydsl:querydsl-apt:${queryDslVersion}"
	implementation "com.querydsl:querydsl-core:${queryDslVersion}"



	runtimeOnly 'com.h2database:h2'

	annotationProcessor 'org.projectlombok:lombok'
	testImplementation 'org.springframework.boot:spring-boot-starter-test'

	//JUnit4 추가
	testImplementation("org.junit.vintage:junit-vintage-engine") {
		exclude group: "org.hamcrest", module: "hamcrest-core"
	}
}

tasks.named('test') {
	useJUnitPlatform()
}
// querydsl 설정
// querydsl 빌드 경로 변수
def querydslDir = "$buildDir/generated/querydsl"

querydsl {
	jpa = true
	querydslSourcesDir = querydslDir
}

// build 시 사용할 sourceSet 추가
sourceSets {
	main.java.srcDir querydslDir
}

configurations {
	querydsl.extendsFrom compileClasspath
}

// querydsl 컴파일시 사용할 옵션 설정
compileQuerydsl{
	options.annotationProcessorPath = configurations.querydsl
}

```





## Lib

`com.querydls:querydsl-apt` : code genration 코드를 만들기 위한 것

`com.querydls:querydsl-jpa` : Application작성할 때 필요한 코드



## QueryDSL 기본문법

#### Q클래스

```java
QMember qMember = new QMember("m"); //별칭 직접 지정
QMember qMember = QMember.member;   //기본 인스턴스 사용
```

```java
import static jpa.practice2.jpa2.domain.queryDSL.QMemberQuery.*;

@Test
public void startQuerydsl(){
	// find member1
	// QMemberQuery m = new QMemberQuery("m");
	MemberQuery findMemberQuery = queryFactory
    		.select(memberQuery)
        	.from(memberQuery)
            .where(memberQuery.username.eq("member1")) 
            // parameter binding을 안해도 자동으로 해준다.
                .fetchOne();
        assertThat(findMemberQuery.getUsername()).isEqualTo("member1");
    }
```

- 기본 인스턴스를 사용 + static import로 바꿔서 사용하면 더 깔끔하게 사용할 수 있음
- **같은 테이블을 조인**할 때는 `QMember qMember = new QMember("m");` 별칭을 사용해서 쓰면 된다.

```yaml
  jpa:
    hibernate:
      ddl-auto: create
    properties:
      hibernate:
        format_sql: true
        default_batch_fetch_size: 100
        use_sql_comments: true
        # 위를 사용하면 jpql이 로그로 찍히게 된다.
```



#### 검색쿼리

ex_

```sql
@Test
public void search(){
    MemberQuery findMember = queryFactory
        .selectFrom(memberQuery)
        .where(memberQuery.username.eq("member1")
               .and(memberQuery.age.eq(10)))
        .fetchOne();
    assertThat(findMember.getUsername()).isEqualTo("member1");
}
```



**검색조건**

```java
member.username.eq("member1") 		// username = 'member1'
member.username.ne("member1") 		// username != 'member1'
member.username.eq("member1").not()  // username != 'member1'
    
member.username.isNotNull() 		// 이름이 is not null
    
member.age.in(10, 20) 			    // age in (10,20) => 10살 이거나 20살
member.age.notIn(10, 20) 			// age not in (10, 20)
member.age.between(10,30) 			// between 10, 30
    
member.age.goe(30) 				    // age >= 30 => 크거나 같거나
member.age.gt(30) 					// age > 30
member.age.loe(30) 					// age <= 30
member.age.lt(30) 					// age < 30
    
member.username.like("member%") 	 // like 검색
member.username.contains("member") 	 // like ‘%member%’ 검색
member.username.startsWith("member") // like ‘member%’ 검색
```



**and => , **

```java
    @Test
    public void search(){
        MemberQuery findMember = queryFactory
                .selectFrom(memberQuery)
//                .where(memberQuery.username.eq("member1")
//                        .and(memberQuery.age.eq(10)))
                .where(memberQuery.username.eq("member1"), // 위 방법과 동일하다.
                        (memberQuery.age.eq(10)))
                .fetchOne();
        assertThat(findMember.getUsername()).isEqualTo("member1");
    }
```

- where() 에 파라미터로 검색조건을 추가하면 AND 조건이 추가됨 
- 이 경우 null 값은 무시 메서드 추출을 활용해서 동적 쿼리를 깔끔하게 만들 수 있음



#### 결과 조회

- **fetch( ) :**  
  - 리스트 조회
  - 데이터 X => 빈리스트 반환

- **fetchOne( )**
  - 결과 없으면 null
  - 둘 이상 => Error

- **fetchFirst( )**
  - limit(1).fetch( )

- **fetchResults( )**
  - 페이징 정보 포함
  - **total count 쿼리 추가 실행**
  - 성능이 중요한 paging을 활용해야할 때는 서로 다른 값을 내보낼 수 있다.
    - 성능 때문에
  - 따라서 이때는 쿼리 두개를 따로 보내야한다.

```sql
@Test
public void resultFetch(){
    QueryResults<MemberQuery> results = queryFactory
        .selectFrom(memberQuery)
        .fetchResults();
        
    # result값을 이용
    # getResults => Contents라고 생각하면 됨
    # 
    results.getResults();
    List<MemberQuery> content = results.getResults();
}
# 이렇게하면 쿼리를 두번 실행
# 1 => total이 있어야 paging할때 어디까지 페이지가 있는지 보여줄 수 있기 때문이다. 
```



- **fetchCount( )**
  - count 쿼리로 변경해서 count 수 조회



#### 정렬

```java
/**
 * 회원 정렬 순서
 * 1. 회원 나이 내림차순(desc)
 * 2. 회원 이름 올림차순(asc)
 * 단 2에서 회원 이름이 없으면 마지막에 출력(nulls last)
 */
@Test
public void sort(){
    em.persist(new MemberQuery(null,100));
    em.persist(new MemberQuery("member5",100));
    em.persist(new MemberQuery("member6",100));

    queryFactory
        .selectFrom(memberQuery)
        .where(memberQuery.age.eq(100))
        .orderBy(memberQuery.age.desc(), memberQuery.username.asc().nullsLast())
        .fetch();
}
```



#### 페이징

```java
// 원하는 곳을 페이징 할 경우
@Test
public void paging1() {
    List<MemberQuery> result = queryFactory
        .selectFrom(memberQuery)
        .orderBy(memberQuery.username.desc())
        .offset(1) //0부터 시작(zero index) => 하나를 스킵한다는 뜻이다.
        .limit(2) //최대 2건 조회
        .fetch();
    assertThat(result.size()).isEqualTo(2);
}

```

```java
// 전체 페이징을 원할 경우
// contents쿼리는 복잡
// count쿼리는 단순하게 짤 수 있을 때가 존재
// 따라서 나눠서 사용하는 것이 좋을 때가 있음
@Test
public void paging2() {
 QueryResults<Member> queryResults = queryFactory
         .selectFrom(member)
         .orderBy(member.username.desc())
         .offset(1)
         .limit(2)
         .fetchResults();
 assertThat(queryResults.getTotal()).isEqualTo(4);
 assertThat(queryResults.getLimit()).isEqualTo(2);
 assertThat(queryResults.getOffset()).isEqualTo(1);
 assertThat(queryResults.getResults().size()).isEqualTo(2);
}
```

-  **주의**
  - count 쿼리가 실행되니 성능상 주의!
    - 데이터를 조회하는 쿼리는 여러 테이블을 조인해야 하지만,  count 쿼리는 조인이 필요 없는 경우도 있다.
    - 이렇게 자동화된 count 쿼리는 원본 쿼리와 같이 모두 조인을 해버리기 때문에 성능이 안나올 수 있다
  - count 쿼리에 조인이 필요없는 성능 최적화가 필요하다면,  count 전용 쿼리를 별도로 작성해야 한다



#### 집합

```java
/**
     * JPQL
     * select
     * COUNT(m), //회원수
     * SUM(m.age), //나이 합
     * AVG(m.age), //평균 나이
     * MAX(m.age), //최대 나이
     * MIN(m.age) //최소 나이
     * from Member m
     */
@Test
public void aggregation() throws Exception {
    // 이렇게 여러가지를 가져오게 될때 => Tuple로 조회하게 된다.
    List<Tuple> result = queryFactory
        .select(memberQuery.count(),   // count
                memberQuery.age.sum(), // 합
                memberQuery.age.avg(), // 평균
                memberQuery.age.max(), // 맥스
                memberQuery.age.min()) // min
        .from(memberQuery)
        .fetch();
    
    Tuple tuple = result.get(0);
    
    assertThat(tuple.get(memberQuery.count())).isEqualTo(4);
    assertThat(tuple.get(memberQuery.age.sum())).isEqualTo(100);
    assertThat(tuple.get(memberQuery.age.avg())).isEqualTo(25);
    assertThat(tuple.get(memberQuery.age.max())).isEqualTo(40);
    assertThat(tuple.get(memberQuery.age.min())).isEqualTo(10);
}
```

- 이렇게 **여러가지**를 가져오게 될때 => **Tuple**로 조회하게 된다.
- DTO로 직접 뽑아오는 방법을 많이 사용하게 된다.



#### GroupBy사용

**group by**

```java
@Test
public void group(){
    List<Tuple> result = queryFactory
        .select(teamQuery.name, memberQuery.age.avg()) // 팀의 이름과 각 팀의 평균 연령
        .from(memberQuery) // member에서
        .join(memberQuery.teamQuery, teamQuery) // member의 팀이랑 팀이랑 조인
        .groupBy(teamQuery.name) // team의 이름과 그룹지어라
        .fetch();
}
```



**+ having**

```java
.groupBy(item.price)
.having(item.price.gt(1000))
```

- item.price로 그룹화해서 뽑아오는데 그것중에서 1000이 넘는 것만 뽑아라



#### 조인(join)

**join**

```java
// 팀A에 소속된 모든 회원
@Test
public void join(){
    List<MemberQuery> result = queryFactory
        .selectFrom(memberQuery)
        .join(memberQuery.teamQuery, teamQuery)
        .where(teamQuery.name.eq("teamA"))
        .fetch();

    assertThat(result)
        .extracting("username")
        .containsExactly("member1","member2");
}
```

- join => inner join
- left join
- right join 모두 가능하다.

**theta join**

- 연관관계가 없는 필드를 조인할 떄 사용한다.
- from을 이용함

```java
// 연관관계가 없는 것들을 조인할때 사용
// 회원이름과 팀이름이 같은 이름을 찾는다고 가정
// from 절에다가 값을 넣게 된다. => cross join을 해버림
@Test
public void theta_join(){
    em.persist(new MemberQuery("teamA"));
    em.persist(new MemberQuery("teamB"));
    em.persist(new MemberQuery("teamC"));

    List<MemberQuery> result = queryFactory
        .select(memberQuery)
        .from(memberQuery, teamQuery)
        .where(memberQuery.username.eq(teamQuery.name))
        .fetch();

    assertThat(result)
        .extracting("username")
        .containsExactly("teamA","teamB");
}
```

- 외부 조인이 불가능 했음 => 하지만 on을 사용하면 가능하다.



#### 조인 -on절

**On절 활용**

- 조인 대상 필터링
  - inner join일때는 where을 사용할 수 있어서 where을 사용하지만
  - outer join일때는 where을 사용할 수 없기 때문에 on을 사용한다.  => 정말 필요한 경우

```sql
public void join_on_filtering(){
    List<Tuple> result = queryFactory
        .select(memberQuery, teamQuery)
        .from(memberQuery)
        .leftJoin(memberQuery.teamQuery, teamQuery) # member에 있는 team을 team이랑 조인
        .on(teamQuery.name.eq("teamA"))
        .fetch();
    for (Tuple tuple : result) {
        System.out.println("tuple : "+ tuple);
}

/*
tuple : [MemberQuery(id=83, username=member1, age=10), TeamQuery(id=81, name=teamA)]
tuple : [MemberQuery(id=84, username=member2, age=20), TeamQuery(id=81, name=teamA)]
tuple : [MemberQuery(id=85, username=member3, age=30), null]
tuple : [MemberQuery(id=86, username=member4, age=40), null]
*/
```

- 그럼 여기서 만약에 inner join을 한다면? => 교집합
  - 밑에와 같은 결과가 나온다.

```java
/*
tuple : [MemberQuery(id=83, username=member1, age=10), TeamQuery(id=81, name=teamA)]
tuple : [MemberQuery(id=84, username=member2, age=20), TeamQuery(id=81, name=teamA)]
*/
```

**연관관계 없는 엔티티 외부 조인**

- 이 경우는 종종 쓰임

```sql
@Test
public void join_on_no_relation(){
    em.persist(new MemberQuery("teamA"));
    em.persist(new MemberQuery("teamB"));
    em.persist(new MemberQuery("teamC"));

    List<Tuple> result = queryFactory
        .select(memberQuery, teamQuery)
        .from(memberQuery)
        .leftJoin(teamQuery) # 이 경우가 다르다 
        .on(memberQuery.username.eq(teamQuery.name))
        .fetch();

    for (Tuple tuple : result) {
        System.out.println("tuple : "+ tuple);
    }
}
    #결과
    /*
    tuple : [MemberQuery(id=44, username=member1, age=10), null]
    tuple : [MemberQuery(id=45, username=member2, age=20), null]
    tuple : [MemberQuery(id=46, username=member3, age=30), null]
    tuple : [MemberQuery(id=47, username=member4, age=40), null]
    tuple : [MemberQuery(id=48, username=teamA, age=0), TeamQuery(id=42, name=teamA)]
    tuple : [MemberQuery(id=49, username=teamB, age=0), TeamQuery(id=43, name=teamB)]
    tuple : [MemberQuery(id=50, username=teamC, age=0), null]
    */
```

- 이 경우에 확인할 점
  - leftJoin(memberQeury.teamQuery, teamQuery)  
    이런식으로 사용했지만 위에서는 그렇게 사용하지 않았다.
    이렇게 사용하게 되면 id값으로 매칭을 시키게된다.
  - **leftJoin(teamQuery)** // 이 경우가 다르다
    .on(memberQuery.username.eq(teamQuery.name))
    이 방법으로 진행할 경우 username만 같은지를 확인하게 된다.

- 일반조인
  - **`leftJoin(member.team, team)`**
- **on 조인**
  - **`from(member).leftJoin(team).on(xxx)`**



#### Fetch join 페치조인

- `.join(memberQuery.teamQuery, teamQuery).fetchJoin()`
  - 조인 뒤에 fetchJoin()을 사용하면 사용할 수 있음

```java
@PersistenceUnit
EntityManagerFactory emf;
@Test
public void fetchJoinUse() throws Exception {
    em.flush();
    em.clear();
    MemberQuery findMember = queryFactory
        .selectFrom(memberQuery)
        .join(memberQuery.teamQuery, teamQuery).fetchJoin() //이부분
        .where(memberQuery.username.eq("member1"))
        .fetchOne();
    boolean loaded =
        emf.getPersistenceUnitUtil().isLoaded(findMember.getTeamQuery()); 
    	// 초기화가 된 엔티티인지 아닌지 알려주는 애임
    assertThat(loaded).as("페치 조인 적용").isTrue();


```



#### 서브 쿼리

- com.querydsl.jpa.JPAExpressions 사용를 사용

```java
// 1. 회원중에서 나이가 가장 많은 회원
// 2. 회원의 평균나이보다 많은 회원들
// 3. in절 안에 있는 회원들
// 4. where절 말고 select절 안에도 sub select사용 가능
@Test
public void subQuery(){

    QMemberQuery subMember = new QMemberQuery("subMember");

    List<MemberQuery> result = queryFactory
        .selectFrom(memberQuery)
        .where(memberQuery.age.eq(  // goe, in
            JPAExpressions
            .select(subMember.age.max()) // avg
            .from(subMember) // 변수가 달라야한다.
            // .where(memberSub.age.gt(10))  / in과 관련
        ))
        .fetch();
    assertThat(result).extracting("age").containsExactly(40);
}
```

- JPA 서브쿼리는 from 절에서 서브쿼리가 되지 않는다.
  - 하이버네이트 6절 이상에서 가능한것으로 알고 있다.



#### Case문

- 단순

```java
@Test
public void simpleCase(){
    List<String> fetch = queryFactory
        .select(memberQuery.age
                .when(10).then("열살")
                .when(20).then("스무살")
                .otherwise("기타"))
        .from(memberQuery)
        .fetch();
}
```

- 복잡 조건
  - 조금 복잡할 때는 CaseBuilder를 사용한다.
  - DB에서는 데이터를 퍼올리는데 집중하는 것이 좋다. 
  - 이런 것을 하는 건 DB를 건들이면서 하는 것이 아니라 Application 측에서 하는 것이 좋다.

```java
@Test
public void simpleCase(){
    List<String> fetch = queryFactory
        .select( new CaseBuilder()
                .when(memberQuery.age.between(0,20)).then("0~20")
                .when(memberQuery.age.between(21,30)).then("21~30")
                .otherwise("기타"))
        .from(memberQuery)
        .fetch();
}
```



#### 상수, 문자 더하기

- Expressions.constant(xxx) 사용

**상수 더하기**

```sql
Tuple result = queryFactory
     .select(member.username, Expressions.constant("A"))
     .from(member)
     .fetchFirst();

//결과
/*
tuple = [member1, A]
tuple = [member2, A]
tuple = [member3, A]
tuple = [member4, A]
*/
```

 참고: 위와 같이 최적화가 가능하면 SQL에 constant 값을 넘기지 않는다. 상수를 더하는 것 처럼 최적화가 어려우면 SQL에 constant 값을 넘긴다.

**문자 더하기**

```sql
# username_나이
# 위 같이 만들어서 가져오고 싶을때
String result = queryFactory
         .select(member.username.concat("_").concat(member.age.stringValue()))
         .from(member)
         .where(member.username.eq("member1"))
         .fetchOne();
//결과
/*
s = member1_10
*/
```

- 문자가 아닌 다른 타입들은 `stringValue()` 로 **문자로 변환**할 수 있다
- enum을 처리할 때 자주 사용한다고 한다.

