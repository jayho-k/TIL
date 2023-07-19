# 03_dynamic_query

## 1) `BooleanBuilder`사용

```sql
# Parameter가 바뀔때 마다 쿼리가 바뀌어야할때
# 검색조건
@Test
public void dynamicQuery_BooleanBuilder(){
    String usernameParam = "member1";
    Integer ageParam = 10;
    List<MemberQuery> result = searchMember1(usernameParam,ageParam);
    assertThat(result.size()).isEqualTo(1);
}

/*
(1) username : memberQuery.username = member1
(2) builder : memberQuery.username = member1 && memberQuery.age = 10
*/
private List<MemberQuery> searchMember1(String usernameCond, Integer ageCond){
    BooleanBuilder builder = new BooleanBuilder(); # 확인
    if (usernameCond!=null){
        builder.and(memberQuery.username.eq(usernameCond)); # 이렇게 하면 (1)
        System.out.println("username : "+ memberQuery.username.eq(usernameCond));
    }
    if (ageCond!=null){
        builder.and(memberQuery.age.eq(ageCond));  # 이렇게 하면 (2)
    }
    System.out.println("builder : "+builder);
    return queryFactory
        .selectFrom(memberQuery)
        .where(builder)
        .fetch();
}

```

- 위와 같이 검색쿼리를 사용할 떄 사용하는 것이다.
- `BooleanBuilder builder = new BooleanBuilder();` 이것을 사용
- 이렇게 조건을 추가해서 동적 쿼리를 만들 수 있다.



## 2) `Where` 다중 파라미터 사용

```sql
@Test
public void dynamicQuery_BooleanBuilder(){
    String usernameParam = "member1";
    Integer ageParam = 10;
    List<MemberQuery> result = searchMember2(usernameParam,ageParam);
    assertThat(result.size()).isEqualTo(1);
}

# 결과 부분을 먼저 볼 수 있음
private List<MemberQuery> searchMember2(String usernameCond, Integer ageCond){
    return queryFactory
        .selectFrom(memberQuery)
        .where(usernameEq(usernameCond), ageEq(ageCond)) # 깔끔해진 부분
        .fetch(); 
}

# 여기부턴 같은지 확인하는 부분이다.
private Predicate usernameEq(String usernameCond) {
    return usernameCond != null ? memberQuery.username.eq(usernameCond) : null;
}
private Predicate ageEq(Integer ageCond) {
    return ageCond != null ? memberQuery.age.eq(ageCond) : null;
}
```

- 1번과 똑같은 조건이다
  - 하지만 이렇게 2개의 method를 더 만들어서 사용하게 된다.
- **장점**
  - where절이 더 깔끔해진다.
  - 결과를 먼저 보게 되어 코드를 이해하기 쉬워진다.
  - method로 빠져있기 때문에 재사용이 가능하다는 장점이 있다.
  - 즉 조립을 할 수 있다는 것



## 3) 벌크연산

- **한번에 처리하는 연산**

```sql
@Test
public void bulkUpdate(){
    queryFactory
        .update(memberQuery) #update
        .set(memberQuery.username,"비회원") # 이렇게 바꿀 것이다
        .where(memberQuery.age.lt(28)) # 조건
        .execute(); # 한번에 벌크
}

# 연산
@Test
public void bulkAdd(){
	long count = queryFactory
    	.update(memberQuery)  # delete로 바꾸면 delete로 바뀜
        .set(memberQuery.age, memberQuery.age.add(1)) 
        	# 빼기 => -1 / 곱하기 => multiply / 
        .execute();
}

```

- 나이가 28살 미만인 모든 회원을 비회원으로 바꿔라
  - `.execute()`
- **조심해야 할 점**
  - `PersistanceContext`를 적재적소에 잘 초기화 해줘야 한다.
  - 즉 DB에서 먼저 반영 => 즉 초기화 해주고 코드작성
    - `em.flush();`
    - `em.clear();`

여담 : `@Commit` :  
이것을 사용하면 Transactional에서 자동으로 rollback을 하는데 이것을 사용하면 commit을 하게된다. 
즉 Test할때 이것으로 DB값을 확인할 수 있다.



## SQL function호출











