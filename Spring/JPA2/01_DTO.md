# 01_DTO

## DTO를 써야하는 이유

- Entity의 스펙이 바뀌게 되기 때문에 Entity를 직접적으로 사용하는 것을 지향해야함
- 따라서 별도의 **request와 response**를 만들어 줘서 만드는 것이 좋음 **(DTO)**
- 나중에 큰 장애가 발생하게 된다.
- **Entity는 외부에 노출하는 것이 아니다.**
  - 엔티티의 모든 값이 노출되게 된다.

- 어떤 API는 name이 필요하지만 어떤 API에서는 name이 필요없을 수 있다.
  - 따라서 요구에 맞춰서 값을 가져와주는것이 좋다.


```java
public CreateMemberResponse saveMemberV2(@RequestBody @Valid CreateMemberRequest request){
        Member member = new Member;
        member.setName(request.getName());
        Long id = memberService.join(member);
        return new CreateMemberResponse(id);
    }
```

- 또한 어떤 스펙에서는 name을 꼭 받아와야하고 어떤 스펙에서는 name이 필요없는 경우가 있다.
  - 그렇게 한다면 NotEmpty를 사용하기가 애매해진다.

```java
@Data
static class CreateMemberRequest{
    @NotEmpty
    private String name;
}

```

- 따라서 이런식으로 별도의 DTO를 만들어서 사용하면 @NotEmpt를 필요할때마다 만들어주면 된다.

@Put은 같은걸 여러번 호출하더라고 변경이 되지 않는다. 하지만 POST경우 값을 보내면 변경시키게 된다. 효율면에서 update를 할때 put이 좋음



## Result 클래스로 컬렉션 감싸기

```java
@Data
 @AllArgsConstructor
 static class Result<T> {
 private T data, count;
 }
```

- 이런식으로 사용해줘야 유연하게 json값을 대체해서 넘길 수 있게 된다.
- ex
  - data의 값과 count의 값이 필요할때 추가로 보내주면 된다는것
