# 04_singleton



## 싱글톤 패턴이란?

- 클래스의 인스턴스가 1개만 생성됨을 보장하는 디자인패턴
- 즉 인스턴스를 2개 이상 생성하지 못하도록 막아야한다.
  - private 생성자를 사용 ==> 외부에서 임의로 new키워드를 못하도록 막는다.

```java
public class SingletonService{
    
    // 1. 자기자신을 객체로 생성
    private static final SingletonService instance = new SingletonService();
    
    // 2. public으로 열고, 인스턴스가 필요하면 이 static 매서드를 통해서만 조회가능
    public static SingletonService getInstance(){
        return instance;
    }
    
    // 3. 생성자를 private으로 선언 
		// => 외부에서 new 키워드를 사용한 객체 생성을 못하게 막음
   	private SingletonService(){}
    
}
```

1. 자기자신을 객체로 생성
   - private, static final 사용
   - static 영역에 객체 instance를 미리 하나 생성해서 올려둔다.
   - private이기 때문에 외부에서 접근 불가능
   - final이기 때문에 변경되지 않는 값을 가짐
     - **즉! 외부 접근 x + 하나만 존재 + 변경되지 않음**
2. public으로 열고, 인스턴스가 필요하면 static매서드를 통해서만 조회가능
3. private으로 new로 선언 못하게 막아머림



## 문제점

- DIP위반 => 클라이언트가 구현체 클래스에 의존
  - getInstance해서 불러와야하기 때문에
- private생성자로 사용함 ==> 자식 클래스를 만들기 힘듦
- 안티 패턴으로 불림













