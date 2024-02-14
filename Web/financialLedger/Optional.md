# Optional

> - https://mangkyu.tistory.com/70
> - https://easybrother0103.tistory.com/39
> - 

## 01_Optional이란

- Wrapper 클래스로 null이 오는 값을 각종 함수로 처리해줄 수 있는 객체이다.



## 02_Optional 사용 예시

### 02-1 ) Optional.of()

- Null이 절대 아니어야 할때 사용한다.

```java
// Optional에 null을 저장할 시 NPE 발생
Optional<String> optional = Optional.of("MyName");
```



### 02-2) Optional.ofNullable()

```java
// 값이 Null일수도 있고 아닐수도 있을때 사용
Optional<String> optional = Optional.ofNullable(getName());

// 값이 없다면(null)이면 익명으로 저장
optional.orElse("익명"); 
```



02-3) .map, orElse

```java
// Before
public String findPostCode() {
    UserVO userVO = getUser();
    if (userVO != null) {
        Address address = user.getAddress();
        if (address != null) {
            String postCode = address.getPostCode();
            if (postCode != null) {
                return postCode;
            }
        }
    }
    return "우편번호 없음";
}

// After
String result = user.map(UserVO::getAddress)
    .map(Address::getPostCode)
    .orElse("우편번호 없음");

```



## 03_orElse와 orElseGet차이

> - 차이점
>   - orElse : 파라미터로 **값**을 받음
>   - orElseGet : 파라미터로 **함수형 인터페이스**를 받는다.

```java
public void findUserEmailOrElse() {
    String userEmail = "Empty";
    String result = Optional.ofNullable(userEmail)
    	.orElse(getUserEmail());
        
    System.out.println(result);
}

public void findUserEmailOrElseGet() {
    String userEmail = "Empty";
    String result = Optional.ofNullable(userEmail)
    	.orElseGet(this::getUserEmail);
        
    System.out.println(result);
}

private String getUserEmail() {
    System.out.println("getUserEmail() Called"); // 이부분이 다름
    return "mangkyu@tistory.com";
}


// 1. orElse인 경우
getUserEmail() Called
Empty

// 2. orElseGet인 경우
Empty
```

- orElse

  - Optional.ofNullable(userEmail)로 EMPTY를 갖는 Optional 객체 생성

  - getUserEmail() 함수가 직접 실행이 된 뒤 orElse로 파라미터를 전달한다.

  - orElse가 호출된다. => 값이 Null이 아니기 때문에 Empty를 가지게 된다.

    

- orElseGet

  - Optional.ofNullable(userEmail)로 EMPTY를 갖는 Optional 객체 생성
  - getUserEmail() 함수 자체를 orElseGet파라미터로 전달
  - orElse가 호출됨 => Null이 아니기 때문에 EMPTY를 그대로 가지며 getUserEmail이 호출되지 않는다.



```java
// 장애 발생 가능성
public void findByUserEmail(String userEmail) {
    return userRepository.findByUserEmail(userEmail)
            .orElse(createUserWithEmail(userEmail)); 
    // 값이 null일 경우 (user가 없을 경우) 값을 생성해주는 함수이다.
    // 하지만 여기서 orElse는 일단 함수를 호출하고 난뒤에 로직이 처리된다.
    // 따라서 값이 존재한다고 하더라고 createUserWithEmail가 실행되며 새로운 값을 
	// 넣으려고 할 것이다. ==> 에러가 발생하게 된다.
}

private String createUserWithEmail(String userEmail) {
    User newUser = new User(userEmail); // uniqe한 user
    return userRepository.save(newUser);
}

```

- ==> 위같은 경우 ElseGet으로 변경해야한다.
- ==> 또한 Cost가 높으므로 orElseGet을 선호한다.
- **값일때는 Else, 함수일때는 orElseGet으로 고려해봐도 좋을듯 하다.**



## 04_올바른 활용법

> - Optional 변수에 Null을 할당하지 말것
> - 값이 없을 때 Optional.orElseX()로 기본 값을 반환할 것
> - 단순히 값을 얻으려는 목적으로만 Optional을 사용할 것
> - 생성자, 수정자, 메소드 파라미터 등으로 Optional을 넘기지 말 것
> - Collection의 경우 Optional이 아닌 빈 Collection을 사용할 것
> - 반환 타입으로만 사용할 것



### Optional 변수에 Null을 할당하지 말것

- Optional 자체가 null인지 또 확인하는 상태가 발생
- Optioanl.empty로 초기화 할 것



### 값이 없을 때 Optional.orElseX()로 기본 값을 반환할 것

- 가급적 isPresent를 사용해서 if문을 만들지 말고 orElse과 같은 함수를 사용하는게 좋다. 
  왜냐하면 깔끔!



### 단순히 값을 얻으려는 목적으로만 Optional을 사용할 것

- 굳이 사용하지 않아도 될 곳에 사용하지 말자

```java
// AVOID
public String findUserName(long id) {
    String name = ... ;
    
    // Optional 클래스로 한번 감싸게 되는 것
	// ==> cost가 너무 비싸기 때문에 아래와 같이 진행하자
    return Optional.ofNullable(name).orElse("Default"); 
    
}

// PREFER
public String findUserName(long id) {
    String name = ... ;
    
    return name == null 
      ? "Default" 
      : name;
}
```



### 생성자, 수정자, 메소드 파라미터 등으로 Optional을 넘기지 말 것

- 값에 대한 null check를 또 해줘야한다.



### Collection의 경우 Optional이 아닌 빈 Collection을 사용할 것

- Collections.emptyList ()

```java
// AVOID
public Optional<List<User>> getUserList() {
    List<User> userList = ...; // null이 올 수 있음

    return Optional.ofNullable(items);
}

// PREFER
public List<User> getUserList() {
    List<User> userList = ...; // null이 올 수 있음

    return items == null 
      ? Collections.emptyList() // 이런식으로 emptyList인지 걸러낼 수 있다.
      : userList;
}
```



### 반환 타입으로만 사용할 것

- optional은 null을 걸러내기 위해서 설계된 것이다. 따라서 Null이 될지에 대해서만 생각하자



## 05_Optional을 통한 예외처리 

```java
// Before
public Long join(Member member) {

    //중복 예외처리
    Optional<Member> result = memberRepository.findById(member.getId());

    result.ifPresent(m -> {
        throw new IllegalStateException("이미 존재하는 회원입니다.");
    });
}


// After
public Long join(Member member) {

    // Optional 더 깔끔하게
	memberRepository.findById(member.getId())
        .ifPresent(m -> {
            throw new IllegalStateException("이미 존재하는 회원입니다.");
        });;

    this.memberRepository.save(member);
    return member.getId();
}

```



**ifPresentOrElse 활용**

```java
categoryRepository.findCategoryByUserIdAndId(userId, categoryId)
    .ifPresentOrElse(
    category -> {categoryRepository.delete(category);},
    ()-> {throw new IllegalStateException("삭제할 값이 존재하지 않습니다.");}
);
```























