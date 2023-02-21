# Optional

출처

https://mangkyu.tistory.com/70

## 01_Optional이란

- NPE를 방지
- Wrapper class
- 즉 NPE를 방지하기 위한 Wrapper class



## 02_ 

**.empty( )**

```java
Optional<String> optional = Optional.empty();
// optional => Opeional.empty
// optioanl.isPresent() => false
```

- `optioanl.isPresent()`을 할시에 false 값이 뜬다.



**.ofNullable( )** 

- 값이 null일 수도 있고 아닐 수도 있는 경우

```java
Optional <String> optional = Optional.ofNullable(getName());
String name = optional.orEsle("익명") // 값이 없다면 익명이라고 리턴
```

























