# jvm

- jvm : 자바 프로그램을 실행하기 위한 환경을 제공
  - 자바 바이트 코드를 로드
     => 바이트 코드 검증 (바이트 코드 검증기에서 코드의 유효성 검사)
     => 준비 (필요한 메모리 할당)
     => 해석 , 실행 (바이트코드를 명령어 단위로 읽어서 실행)
     => 자바 애플리케이션의 실행 환경을 관리
  - class loader : 로드
    - 자바 클래스를 로드
    - 컴파일러에서 컴파일한 자바 클래스(.class)를 JVM으로 로딩하는 역할
    - 로딩을 할 때 바이트 코드 검증까지 한다. (보안성)
    - 메모리에 적재해서 실행 가능한 상태로 만든다.
  - 런타임 데이터 영역 
    - 프로그램을 실행하기 위해서 OS에서 할당받은 메모리 (how? 얼마나?)
    - 메서드 영역 :
      - 클래스 정보
      - 메소드 정보
      - 상수 풀
    - 힙 : 
      - 런타임이 동적으로 할당되는 모든 객체와 배열을 저장
      - 가비지 컬렉터에 의해서 관리
    - 스택 : 
      - 스레드 메서드 호출, 로컬 변수
      - 메소드 호출 시 생성되는 스택 프레임을 저장
    - 프로그램 카운터() : 
      - 현재 실행 중인 JVM명령의 주소를 저장하는 공간
      - 현재 작업하는 내용을 CPU에게 연산으로 제공해야한다. 이를 위해서 버퍼공간으로 사용한다. 
      - 자바 메소드를 수행 => JVM의 주소를 PC Register에 저장한다.
      - 다른 언어(C, 어셈들리)의 메소드를 수행하고 있다면, undefined 상태가 된다.
      - 두 경우를 따로 처리하기 때문
    - 네이티브 메서드 스택
      - 자바 외 언어(C,C++, 어셈블리 등)로 작성된 네이티브 코드를 실행하기 위한 메모리 영역
      - 실제 실행할 수 있는 기계어로 작성된 프로그램을 실행시키는 영역
      - JIT 컴파일러에의해 변환된 Native Code 도 여기서 실행된다고 보면 된다.
      - 메소드를 실행 => JVM 스택에 쌓이다가 해당 메소드 내부에 네이티브 방식을 사용하는 메서드가 있어? => 해당 메소드를 네이티브 스택에 쌓음 => 다시 자바스택으로 돌아와서 작업을 수행
      - 그래서 네이티브 코드로 되어있는 함수의 호출을 자바 프로그램 내에서도 직접 수행할 수 있음
      - JNI가 사용되면 네이티브 메서드 스택에 바이트 코드로 전환되어 저장되게 된다.
  - 실행 엔진 : 바이트코드를 실행
    - 로딩된 클래스 파일의 바이트 코드를 해석하고 실행한다.
    - 기계어로 해석된다.
    - 인터프리터는 바이트코드를 한 줄씩 실행하고, JIT컴파일러는 반복되는 코드를 캐싱하여 성능을 개선한다.
    - 인터프리터
      - 바이트 코드 명령어를 하나씩 읽어서 해석하고 실행
      - 호출이 될 때마다 매번 해석하고 수행해야한다.
    - JIT(Just-in-Time) 컴파일러
      - 반복되는 코드를 발견해서 바이트 코드 전체를 컴파일하여 Native Code로 변경 후 캐싱
      - 네이티브 코드(C,C++,assambly로 구성된 코드)로 직접 실행하는 방식
      - Native로 변환하는데 비용이 많이 듦 => 일정 기준이 넘어가면 JIT 컴파일을 사용
  - JNI : 
    - 자바 애플리케이션과 호스트 운영체제간의 상화작용을 가능하게 함
    - 외부 코드와의 연결을 가능하게 해주는 것
    - JVM이 Native Method를 적재하고 수행할 수 있도록 한다.



JVM : 로드, 실행, 저장하고 있는 부분으로 나뉘는데  로드는 classloader 가 담당하고 있고 실행하는 부분은 excution이 맡고 있고, 저장하는 부분은 runtime data area에서 맡고 있다

- class loader
  - (.class)들을 엮어서 JVM의 메모리 영역인 Runtime Data Area에 배치하는 역할
  - 로딩을 한번에 메모리에 올리는게 아니라 애플리케이션이 필요할 때 동적으로 올려줌
  - Loading(JVM 메모리에 로드) >> Linking(검증) >> Initailizing(클래스 변수 초기화, static 필드들을 설정된 값으로 초기화 등)
    - Linking : 
      - Verifying(읽어들인 클래스가 JVM 명세에 명시된 대로 구성되어있니?)
      - Preparing(클래스가 필요로 하는 메모리를 할당)
      - Resolving(클래스의 상수 풀 내 모든 심볼릭 레퍼런스를 다이렉트 레퍼런스로 변경)
        - Symbolic Reference : 
          - 프로그램 내에서 클래스, 메서드, 필드 등을 직접적으로 식별하는 데 사용되는 이름, 식별자를 말한다. 
          - 컴파일된 바이트 코드 내에 존재, 프로그램 실행 시점에 실제 물리적 메모리 주소로 변환된다.
          - 그래서! 프로그램이 메모리 내에서 객체나 클래스에 접근할 수 있게 된다.
          - 특정 자원을 참조하는 고수준의 이름, 문자열, 식별자이다.
          - JVM이 클래스 파일을 해석하느 과정에서 사용
        - Direct Reference : 



- Symbolic Reference

  - JVM이 .class를 해석할 때 필요함
  - 컴파일 시점에 결정 => 런타임 시점에 실제 메모리 주소로 변환

  - 종류
    - 클래스 Symbolic Reference :
      - 다른 클래스, 인터페이스를 참조하는 문자열.
      - 패키지 경로, 클래스 이름으로 구성 
      - import java.util.ArrayList 
    - 필드 Symbolic Reference
      - 필드의 이름, 소속 클래스 정보
    - 메서드 Symbolic Reference
      - 메서드 이름, 매개변수 타입, 리턴 타입 등

- 싱



 **Code Cache(Non‑Heap)**



```
package com.example;

// JVM 어떤 구성 요소를 가지고 있는지
// load, excute, save 하는 역할로 나뉨
// 
// JVM이 메모리를 어떤 식으로 구분하고 있는지
// class A는 어떤 식으로 로드되는지에 대해서
// classloader란?
class A {
	static : method area에 값을 넣는 과정이라고 이해(변할 수도 있으니 초기화 때 진행)
	static final : method area에 값을 넣는데 어차피 변하지도 않아서 처음부터 넣어주는 느낌
	
    private static final String STR = "ABC";
    private static Long l = Long.valueOf(-1L); // static class, valueOf : static method
    private static int i = -1;
    private static C c = new C();

    private final String a = "ABC";
    private final int ii = 1;
    private C cc = new C();

    public static void main(String[] arg) {
        // JVM Memory에서 무슨 일이 일어나는지 설명해 봅시다.
        A a = new A();
        B b = new B();
        
    }
}

class B extends A {
    
    // ...
}

class C {
    // ...
}
```





- JVM 어떤 구성 요소를 가지고 있는지
  - load, excute, save 하는 역할로 나뉨
    - load : classloader
      - class를 load하는 역할
      - 모델 : 부모 모델 => jdk 9부터 바뀌었음 : 플랫폼 class loader 
      - application, platform에서 클래스 로더 load하라는 말이 오면 거기에 속한 패키지가 있는지 확인하고 위로 던짐
    - execute : excute engine
      - .class 파일을 해석하는 역할 : 
      - 해석?? : 심볼 참조 => 직접 참조로 변환하는 역할
      - 이미 한번 해석이 됐으면 네이티브 데이터 영역에 
    - save : runtime data area
  - 















