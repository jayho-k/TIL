# 06_annotation

### reflection만으로 힘든 이유

- `/site1` 이라는 path가 와도 page1() 과 같은 메서드를 호출하고 싶다면 불가능하다.
- `/`와 같은 자바메서드 이름으로 처리하기 어려운 url을 처리할 수 없다.
- url은 주로 `-`를 사용해서 구분하는데 메서드로 만들 수 없다.



## Annotation이란

- 애노테이션은 코드가 아니다.
- Annotation은 일반적으로 "주석" 또는 "메모"를 의미한다.
- 컴파일러나 렁타임에서 해석될 수 있는 메타데이터를 제공한다.
- 리플레션 같은 기술로 실행 시점에 읽어서 활용할 수 있다. 



## Annotation 정의

```java
@Retention(RetentionPolicy.RUNTIME)
public @interface AnnoElement {

    // java가 제공한 type만 선언할 수 있다.
    // 직접 만든 type은 선언할 수 없다.
    String value();
    int count() default 0;
    String[] tags() default {};

    // MyLogger data(); 다른 타입은 적용 x
    Class<? extends MyLogger> annoData() default MyLogger.class;

}

```

### 정의 규칙

- **데이터 타입**

  - 기본 타입 (int, float ...)

  - String

  - Class(메타데이터) 또는 인터페이스

  - enum

  - 다른 애노테이션 타입

  - 앞서 설명한 타입 외에는 정의할 수 없다. 쉽게 이야기해서 일반적인 클래스를 사용할 수 없다.

    - Member, User 등

      

- **defualt 값**

  - 요소에 defualt 값을 지정할 수 있음

    

- **요소 이름**

  - 메서드 형태로 정의

  - 괄호 ()를 포함하지만 매개변수는 없어야한다.

    

- **반환 값**

  - void를 반환타입으로 할 수 없음

    

- **예외**

  - 선언 불가

    

- **특별한 요소 이름**

  - value라는 이름의 요소를 하나만 가질 경우, 애노테이션 사용 시 요소 이름을 생략할 수 있다.



## Meta Annotation

> - @Retention
> - @Target
> - @Documented
> - @Interited

### @Retention

- 애노테이션의 **생존 기간**을 지정한다

```java
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.ANNOTATION_TYPE)
public @interface Retention {
    RetentionPolicy value();
}
```

```java
public enum RetentionPolicy {
    SOURCE,
    CLASS,
    RUNTIME
}
```

- `SOURCE` : 소스 코드에만 남아있다. 즉 컴파일 시점에 제거된다. (진짜 주석같은 느낌인가..?)
- `CLASS` : 컴파일 후 class 파일까지는 남아있지만 자바 실행 시점에 제거된다. (defualt)
- `RUNTIME` : java 실행 중에도 남아있다.



### @Target

```java
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.ANNOTATION_TYPE)
public @interface Target {
    /**
     * Returns an array of the kinds of elements an annotation interface
     * can be applied to.
     * @return an array of the kinds of elements an annotation interface
     * can be applied to
     */
    ElementType[] value();
}
```

```java
public enum ElementType {
    TYPE,
    FIELD,
    METHOD,
    PARAMETER,
    CONSTRUCTOR,
    LOCAL_VARIABLE,
    ANNOTATION_TYPE,
    PACKAGE,
    TYPE_PARAMETER,
    TYPE_USE,
    MODULE,
    RECORD_COMPONENT;
}
```

- Annotation을 쓸 수 있는 부분을 정해주는 것
- Type으로 지정하면 class에만 붙힐 수 있다는 뜻이다.



### @Documented

- 자바 API 문서를 만들 때 해당 애노테이션이 함께 포함되는지 지정한다. 



### @Ingerited

- 애노테이션을 적용한 클래스의 자식도 해당 애노테이션을 부여받을 수 있다.
- **이 기능은 클래스 상속에서만 작동하고, 인터페이스의 구현체에는 적용되지 않는다.**

```
class annotation.basic.inherited.Parent
 - InheritedAnnotation
 - NoInheritedAnnotation

class annotation.basic.inherited.Child
 - InheritedAnnotation

interface annotation.basic.inherited.TestAnno
 - InheritedAnnotation
 - NoInheritedAnnotation

// 구현체는 interface의 애노테이션이 적용되지 않음
class annotation.basic.inherited.TestAnnoImpl 

```

- @Inherited가 클래스 상속에만 적용되는 이유
  - 인터페이스는 메서드의 시그니처만 정의할 뿐, 상태나 행위를 가지지 않기 때문에, 인터페이스의 구현체가 애노테이션을 상속한다는 개념이 맞지 않음
  - 다중 구현이 가능하기 떄문에 여러 인터페이스의 애노테이션 간의 충돌이나 모호한 상황이 발생할 수 있음







