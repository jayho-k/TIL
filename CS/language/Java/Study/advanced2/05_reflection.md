# 05_reflection



### reflection이 필요한 이유

> **커맨드 패턴의 2가지 단점**
>
> - 하나의 클래스에 하나의 기능만 만들 수 있다.
> - 새로 만든 클래스를 URL 경로와 항상 매핑해야한다.

- 위 두가지를 해결하기 위해 reflection을 사용한다.
- 일반적으로 **테스트나 라이브러리 개발** 같은 특별한 상황에서 유용하게 사용된다.





## Class와 MetaData

> - 클래스가 제공하는 다양한 정보를 동적으로 분석하고 사용하는 기능
> - 프로그램 실행 중에 class, method, field 등에 대한 정보를 얻거나, 새로운 객체를 생성하고 method를 호출하며, field 값을 읽고 쓸 수 있다.

**Reflection을 통해 얻을 수 있는 정보**

- **클래스의 메타데이터** : 클래스 정보(이름, 접근제어자, 부모 클래스 등등)
- **필드 정보** : 필드 정보(이름, 타입, 접근제어자)를 확인하고 해당 필드의 값을 읽거나 수정할 수 있음
- **메서드 정보** : 메서드 정보(이름, 타입, 정보 등)을 확인하고 실행 중에 동적으로 메서드를 호출 할 수 있음
- **생성자 정보** : 생성자의 매개변수 타입과 개수를 확인하고, 동적으로 객체 생성



### reflection

```java
   public static void main(String[] args) throws ClassNotFoundException {
        
        // 1. 클래스 찾기
        Class<BasicData> basicDataClass = BasicData.class;
        System.out.println(basicDataClass);

        // 2. 인스턴스에서 찾기
        BasicData basicInstance = new BasicData();
        // 자식 클래스도 올 수 있기 떄문에 extends를 사용하게 된다.
        Class<? extends BasicData> basicDataClass2 = basicInstance.getClass();
        System.out.println(basicDataClass2);

        // 3. 문자로 찾기
        String className = "reflection.data.BasicData";
        Class<?> basicDataCLass3 = Class.forName(className);
        System.out.println(basicDataCLass3);

    }
```



```java
public class BasicV2 {

    public static void main(String[] args) throws ClassNotFoundException {

        Class<BasicData> basicData = BasicData.class;
        System.out.println("basicData.getName() = " + basicData.getName());
        System.out.println("basicData.getSimpleName() = " + basicData.getSimpleName());
        System.out.println("basicData.getPackage() = " + basicData.getPackage());
        System.out.println("basicData.getSuperclass() = " + basicData.getSuperclass());
        System.out.println("basicData.getInterfaces() = " + Arrays.toString(basicData.getInterfaces()));
        System.out.println("basicData.isInterface() = " + basicData.isInterface());
        System.out.println("basicData.isEnum() = " + basicData.isEnum());
        System.out.println("basicData.isAnnotation() = " + basicData.isAnnotation());

        int modifiers = basicData.getModifiers();
        System.out.println("basicData.getModifiers() = " + modifiers);
        System.out.println("isPublic = " + Modifier.isPublic(modifiers));
        System.out.println("Modifier.toString() = " + Modifier.toString(modifiers));
    }

}
```

```
basicData.getName() = reflection.data.BasicData
basicData.getSimpleName() = BasicData
basicData.getPackage() = package reflection.data
basicData.getSuperclass() = class java.lang.Object
basicData.getInterfaces() = []
basicData.isInterface() = false
basicData.isEnum() = false
basicData.isAnnotation() = false
basicData.getModifiers() = 1
isPublic = true
Modifier.toString() = public
```

- Modifier
  - 수정자가 조합된 숫자를 얻고, Modifier를 사용해서 실제 수정자 정보를 확인할 수 있다.
  - 수정자 : public, private, static 등등



## 동적 메소드

```java
public class MethodV2 {

    public static void main(String[] args) 
        throws NoSuchMethodException, InvocationTargetException, IllegalAccessException {

        // 정적 메서드 호출 - 일반적인 메서드 호출
        BasicData helloInstance = new BasicData();
        helloInstance.call();

        // 동적 메서드 호출 방법
        // 1. class 가져오기
        Class<? extends BasicData> helloClass = helloInstance.getClass();
        String methodName = "hello";
        
        // 2. 가져온 class에서 method 가져오기
        Method method1 = helloClass.getDeclaredMethod(methodName, String.class);
        
        // 3. 가져온 method에서 인스턴스와 인자 넘겨줘서 method호출하기
        Object returnValue = method1.invoke(helloInstance, "hi");
        System.out.println("returnValue = " + returnValue);

    }

}
```



## private field 접근하기 = setAccessable

```java
public class FieldV2 {

    public static void main(String[] args) throws NoSuchFieldException, IllegalAccessException {

        User user = new User("id1", "userA", 20);
        System.out.println(user.getName());

        Class<? extends User> aClass = user.getClass();
        Field nameField = aClass.getDeclaredField("name");

        // private field에 접근을 허용하면 접근가능
        nameField.setAccessible(true); 
        nameField.set(user, "userB");
        System.out.println("변경 된 이름 = " + user.getName());

    }
    
}
```



## 활용 예제

- 데이터를 저장해야하는데, 저장할 때는 방드시 null을 사용하면 안될 경우
- String : ""  /  Integer : 0 으로 변경한다.

```java
public class FieldV4 {

    public static void main(String[] args) 
        throws NoSuchFieldException, IllegalAccessException {

        User user = new User("id1", null, null);
        Team team = new Team("team1", null); // null이 들어가 있음

        System.out.println("user = " + user);
        System.out.println("team = " + team);

        FieldUtil.nullFieldToDefault(user);
        FieldUtil.nullFieldToDefault(team);

        System.out.println("user = " + user);
        System.out.println("team = " + team);
    }
}

// result
user = User{id='id1', name='null', age=null}
team = reflection.data.Team@70177ecd
user = User{id='id1', name='', age=0}
team = reflection.data.Team@70177ecd

```

```java
public class FieldUtil {

    public static void nullFieldToDefault(Object target) throws IllegalAccessException {

        Class<?> aClass = target.getClass();
        Field[] declaredFields = aClass.getDeclaredFields();
        for (Field field : declaredFields) {
            field.setAccessible(true);
            if (field.get(target) != null) {
                continue;
            }
            if (field.getType() == String.class) {
                field.set(target, "");
            } else if (field.getType() == Integer.class) {
                field.set(target, 0);
            }
        }
    }
}
```

- 이렇게 사용하게 되면 모든 class에 null 값을 다른 기본값으로 바꾸는 행위를 하지 않아도 된다.













