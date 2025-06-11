# Thread



## Thread란?

- Light Weight Process 라고도 불린다. 

- 프로세스 : 자원을 할당받아 그것을 제어하는 일을 담당

  - thread : 자원을 제어하는 담당을 맡고 있다.
  - 하나의 애플리케이션(프로세스)에서 여러 실행 흐름을 제어하는 것

  - stack은 개별로 가지고 있고 ,나머지는 메모리 공간(heap, code 등)은 공유한다. 

  

## Thread의 종류

> - hw thread
> - user level thread
> - os kernel thread

### hw thread

- 실행단위같은거라고 보면 됨 : compute작업을 하다가 memory 접근하는 일이 있으면 걔 재우고 다른 일 해야하니깐 생겨난 개념이다.

- OS 입장에서는 각 스레드를 하나의 코어로 인식하게 된다.

- 따라서 듀얼 코어의 hyper thread가 적용된 거라면 os는 core 4개짜리로 인식

  

### User level Thread 

- 스레드 개념을 프로그래밍 레벨에서 추상화한 것이 User thread다.

- ```java
  Thread thread = new Thread();
  ```

- start0가 실행되게 되면 JNI에서 system call을 실행하게 된다.

  - 리눅스 라면 clone이라는 system call을 호출
  - 그럼 os level에서의 thread를 하나 생성하게 된다.

- **user thread가 CPU에서 실행되려면 반드시 OS thread와 연결되어있어야한다.**



### OS Thread (kernel)

- OS 커널에서 생성되고 관리되는 스레드
  - 커널이란
    - 시스템의 전반을 관리, 감독
    - 하드웨어와 관련된 작업을 직접 수행
- CPU에서 실제로 실행되는 단위, CPU 스케줄링의 단위
- OS 스레드의 컨텍스트 스위칭은 커널이 개입 >> 비용 발생
  - 왜냐하면 TCB에 어디까지 작업했는지에 대한 데이터랑 TID 등을 저장해놓고 wait 상태로 ㅏ꿔야하기 때문이다.
  - 이때 thread의 현재 실행상태를 저장하고 새로운 thread를 load시키는 일을 해야함
- 사용자 코드와 커널 코드 모두 OS thread에서 실행된다.
  - 동작
    - 사용자 코드가 OS thread에서 실행이 되고있음 (user mode)
    - system call (kernel mode)로 인해 kernel code가 실행되게 된다.
    - 다시 user mode로 돌아오면 사용자 코드가 실행되게 된다.



### user thread와 OS Thread의 연결 방법

**1:1 모델**

- 사용자 영역에서 thread를 만들게 되면 커널에서도 thread를 만드는 것 (1:1) mapping

- 스레드 관리를 OS에 위임하게 된다. ==> 스케줄링도 커널이 수행하게된다.

- 한 스레드가 블록이 돼도 다른 스레드들은 잘 동작하게 된다.

- race condition 가능성이 존재한다.

- 이렇게 되면 TCB(Thread Control Block)도 커널로 내려오게 된다.

  - 오버헤드가 크다

    - 커널이 각 스레드를 개별적으로 관리가 가능하다.

      - 자기 일을 할 수 있게 된다.

      

**n:1 모델**

- 스레드 라이브러리로 구현 됨
- 유저간의 스위칭 빠름
- 멀티 코어 활용 못함
- 한 Thread가 Block되면 모든 스레드가 block이 되게 된다. 따라서 Non Block IO를 사용한다.
- 커널은 스레드의 존재를 모름
  - 장점 : 커널의 관리(개입)을 받지 않음
    - 생성 및 관리의 부하가 적음, 유연한 관리가 가능
    - 이식성이 높음 / 우리가 만든 thread가 존재
  - 단점 : 커널은 프로세스 단위로 자원 할당
    - 하나의 스레드가 BLOCK 상태가 되면 모든 스레드가 대기(single threaed kernel의 경우)
    - thread하나가 IO가 필요해서 Block상태가 됐다고 하더라도 다른 스레드들은 살아있어서 다른 스레드 들이 일하면 된다. 하지만 커널은 몰라! 커널은 프로세스 단위로 자원을 할당하기 때문이다.



- **n:m 모델**
  - n개 ULT - m개 KLT (n>m)
  - 사용자는 원하는 수 만큼 스레드 사용
  - 커널 스레드는 자신에게 할당된 하나의 사용자 스레드가 block 상태가 되어도 다른 스레드 수행가능 (병렬 처리 가능)
  - 구현이 복잡함



## Context Switch

- Context란?
  - 프로세스/ 스레드의 상태 : CPU, Register, 메모리 주소 공간 등
- 주어진 time slice를 모두 사용했거나, IO 작업, 다른 리소스를 기다리거나 할 때 다른 Thread로 변경하는 것
- Thraed Context Swtich : 같은 process 내에서 서로 다른 스레드끼리 cs를 하는 것

### 특징

- kernel mode에서 실행되게 된다.
- cpu의 레지스터 상태를 교체 (동작하던 중의 정보를 저장)

### 동작 순서

1. CPU 동작이 진행됨
2. time slice or IO로 인한 CS됨
3. user mode => kernel mode
4. T1의 CPU의 레지스터 상태를 저장하게 됨
5. T2의 CPU의 레지스터 상태를 로딩하게 됨
6. kernel mode => user mode



## thread 상태

### OS

- new > read : 바로 read 상태로 감

-  read : CPU에서 실행되기를 기다리는 상태

  - scheduler에 의해서 자기차례가 되면 running 상태가 된다.

- running : CPU의 자원을 사용하게 된다.

- waiting : IO, event wait (critical section등)

  - 여기서 다시 준비가 되게 되면 ready상태로 변경

- terminate 되려면 running 상태로 변경되고 cpu에서 마무리될 준비를 하고 terminate되게 된다.

  

### java thread

- new : 자바 스레드가 아직 시작하지 않은 상태
- runnable
  - 실행 중인 상태
  - 다른 리소스를 기다리는 상태도 포함 : IO작업을 해놓고 기다리는 상태, 
- blocked
  - 모니터 락을 얻기 위해 기다리는 상태
  - critical section으로 들어가려고 모니터락을 얻기 위한 상태
- waiting
  - 다른 스레드를 기다리는 상태
  - object.wait, thread.join 호출될 때
- timed waiting
  - 제한시간을 두고 다른 스레드를 기다리는 상태
  - object.wait with timeout, thread.join with timeout, thread.sleep
- terminated : 실행을 마치고 종료된 상태



## JAVA Thread

### Thread 생성

- `new Thread()` 를 자바에서 생성하고 `thread.start()` 를 하게 되면 `start0` 라는 native 함수를 실행하게 된다. 

- JNI (java native interface) 라는 인터페이스를 통해 해당 C++로 구현된 JVM_StartThread 메소드가 실행

- java thread interface 실행여부를 확인

- call statck 사이즈 확인 후 thread 생성 및 실행

  - ```
    jlong size = java_lang_Thread::stackSize(JNIHandles::resolve_non_null(jthread));
    size_t sz = size > 0 ? (size_t) size : 0;
    native_thread = new JavaThread(&thread_entry, sz);
    ```

  - 네이티스 스레드를 자바 스레드 객체와 연결하고 자바 스레드 실행 준비를 한다.

  - ```
    if(native_thread -> osthread() !=NULL){
    	native_thread->prepare(jthread);
    }
    Thread::start(native_thread);
    ```

  - 결과적으로 Java는 JNI를 통해 실제 OS thread 와 mapping되는 user level의 thread를 획득하게 된다.

  - JNI는 미리 등록된 Thread 클래스의 run() 메소드 시그니처를 실행시킨다. 그래서 사용자가 구현한 메소드가 실제로 JVM상에서 구동되게 된다.

- 



### 쓰레드 관리

쓰레드 관리는 생성부터 종료에 이르는 쓰레드의 전체 생명 주기와 VM 내에서의 쓰레드 간 조율을 포함합니다. 이는 Java 코드(애플리케이션 코드나 라이브러리 코드)에서 생성된 쓰레드, VM에 직접 연결된 네이티브 쓰레드, 그리고 다양한 목적으로 VM 내부에서 생성된 쓰레드들을 모두 포함합니다. 쓰레드 관리의 전반적인 측면은 플랫폼에 독립적이지만, 세부 사항은 기본 운영 체제에 따라 달라집니다.



### 쓰레드 모델

HotSpot의 기본 쓰레드 모델은 Java 쓰레드(`java.lang.Thread` 인스턴스)와 운영 체제의 네이티브 쓰레드 간의 **1:1 매핑**입니다. Java 쓰레드가 시작될 때 네이티브 쓰레드가 생성되며, **쓰레드가 종료되면 네이티브 쓰레드도 회수됩니다.** 운영 체제가 모든 쓰레드의 스케줄링을 담당하고, 가용한 CPU에 작업을 디스패치(프로그램이 어떤 메소드를 호출할지 결정하고 실행하는 과정)합니다.

Java 쓰레드 우선순위와 운영 체제 쓰레드 우선순위 간의 관계는 복잡하며, 시스템마다 다릅니다. 이에 대한 자세한 내용은 뒤에서 다룹니다.



### 쓰레드 생성과 제거

쓰레드는 다음 두 가지 방법으로 VM에 도입될 수 있습니다:

1. Java 코드에서 `java.lang.Thread` 객체에 대해 `start()`를 호출
2. 기존의 네이티브 쓰레드를 JNI를 통해 VM에 연결 (Attach)

또한 VM이 내부 용도로 생성하는 쓰레드들도 존재합니다.

하나의 쓰레드에 대해 VM 내에서는 여러 객체들이 연관되어 있습니다 (HotSpot은 C++로 작성된 객체 지향 시스템입니다):

- `java.lang.Thread` 인스턴스: Java 코드 내에서 쓰레드를 나타냅니다.
- `JavaThread`: VM 내에서 `java.lang.Thread`를 표현하는 객체로, 쓰레드 상태를 추적하는 추가 정보를 포함합니다. `JavaThread`는 `java.lang.Thread` 객체를 참조하며, 반대로 `java.lang.Thread` 객체도 `JavaThread`에 대한 참조를 가지고 있습니다.
- `OSThread`: 운영 체제 쓰레드를 표현하며, 쓰레드 상태를 추적하는 데 필요한 OS 수준의 정보를 담고 있습니다. 이 객체는 운영 체제 쓰레드를 식별하기 위한 플랫폼 종속적인 핸들을 포함합니다.

`java.lang.Thread` 객체가 시작되면, VM은 관련된 `JavaThread`와 `OSThread` 객체들을 생성하고, 궁극적으로 네이티브 쓰레드를 생성합니다. 쓰레드-로컬 저장소, 메모리 할당 버퍼, 동기화 객체 등 VM 상태를 준비한 후 네이티브 쓰레드를 시작합니다. 이 네이티브 쓰레드는 초기화 작업을 마치고 `java.lang.Thread` 객체의 `run()` 메서드를 실행하게 되며, 실행이 끝나면 예외 처리를 포함한 종료 과정을 거쳐 쓰레드를 종료합니다. 쓰레드 종료 시 할당된 리소스가 해제되고, `JavaThread`는 등록된 쓰레드 목록에서 제거되며, `OSThread`와 `JavaThread`의 소멸자가 호출됩니다.

네이티브 쓰레드는 JNI의 `AttachCurrentThread`를 호출하여 VM에 연결할 수 있습니다. 이 호출은 `OSThread`와 `JavaThread`를 생성하고, 기본적인 초기화를 수행합니다. 이후 연결된 쓰레드에 대한 `java.lang.Thread` 객체를 생성해야 하며, 이는 전달된 인자를 바탕으로 Java 코드의 생성자를 리플렉션을 이용해 호출하여 이뤄집니다. 연결된 이후에는 해당 쓰레드가 JNI를 통해 필요한 Java 코드를 호출할 수 있습니다. 더 이상 VM과의 연동이 필요 없게 되면 `DetachCurrentThread`를 호출해 쓰레드와 VM의 연결을 해제합니다(리소스 해제, 객체 참조 제거 등).

특수한 경우로, `CreateJavaVM` JNI 호출을 통해 처음으로 VM이 생성되는 경우가 있습니다. 이는 네이티브 애플리케이션이나 런처(java.c)에서 수행되며, 다양한 초기화 과정을 거친 후 사실상 `AttachCurrentThread`를 호출한 것과 같은 상태가 됩니다. 이후 Java 애플리케이션의 main 메서드를 리플렉션을 통해 호출하는 등 Java 코드를 실행할 수 있습니다. 자세한 내용은 JNI 섹션을 참고하세요.

### 쓰레드 상태

VM은 각 쓰레드가 현재 어떤 작업을 수행 중인지 나타내기 위해 다양한 내부 상태를 사용합니다. 이는 쓰레드 간 상호작용을 조정하거나, 문제가 발생했을 때 디버깅 정보를 제공하는 데 필요합니다. 쓰레드는 특정 작업을 수행할 때마다 상태 전이를 하며, 이 시점에서 현재 작업을 수행해도 되는지 확인합니다. (safepoint 관련 내용 참조)

주요 쓰레드 상태는 다음과 같습니다:

- `_thread_new`: 초기화 중인 새로운 쓰레드
- `_thread_in_Java`: Java 코드를 실행 중인 쓰레드
- `_thread_in_vm`: VM 내부 코드를 실행 중인 쓰레드
- `_thread_blocked`: 잠금 획득, 조건 대기, sleep, 블로킹 I/O 등의 이유로 블록된 쓰레드

디버깅 목적을 위한 추가적인 상태 정보는 `OSThread`에서 관리되며, 다음과 같은 상태들이 있습니다:

- `MONITOR_WAIT`: 모니터 락을 얻기 위해 대기 중
- `CONDVAR_WAIT`: VM 내부 조건 변수에서 대기 중 (Java 객체와는 무관)
- `OBJECT_WAIT`: `Object.wait()` 호출로 인해 대기 중

기타 하위 시스템(JVMTI 등)이나 라이브러리에서도 자체적인 상태 정보를 유지할 수 있으나, 이는 VM 수준의 쓰레드 관리와는 관련이 없습니다.

------

### 내부 VM 쓰레드

단순한 "Hello World" 프로그램을 실행해도 시스템에는 수십 개의 쓰레드가 생성될 수 있습니다. 이는 내부 VM 쓰레드와 라이브러리 관련 쓰레드(예: 참조 처리기, finalizer 쓰레드 등) 때문입니다. 주요 내부 쓰레드는 다음과 같습니다:

- **VM 쓰레드**: `VMThread`의 단일 인스턴스로, VM 작업(VM operations)을 실행합니다.
- **주기적 작업 쓰레드**: `WatcherThread`의 단일 인스턴스로, VM 내에서 주기적인 작업을 수행하기 위해 타이머 인터럽트를 시뮬레이션합니다.
- **GC 쓰레드**: 병렬 또는 동시 가비지 수집을 지원하는 여러 종류의 쓰레드들입니다.
- **컴파일러 쓰레드**: 바이트코드를 네이티브 코드로 JIT 컴파일합니다.
- **시그널 디스패처 쓰레드**: 프로세스 시그널을 대기하고 이를 Java 수준의 핸들러에 전달합니다.

모든 쓰레드는 `Thread` 클래스의 인스턴스이며, Java 코드를 실행하는 모든 쓰레드는 `JavaThread` 클래스의 인스턴스입니다. VM은 모든 쓰레드를 `Threads_list`라는 연결 리스트로 추적하며, 이 리스트는 `Threads_lock`이라는 주요 동기화 락에 의해 보호됩니다.



### VM 작업과 세이프포인트

`VMThread`는 대부분의 시간을 **VMOperationQueue**에서 작업이 대기 중인지 확인하며 기다리다가, 작업이 나타나면 이를 실행하는 데 사용됩니다. 일반적으로 이러한 작업은 **VM이 세이프포인트(safepoint)** 상태에 도달해야만 안전하게 실행할 수 있기 때문에 `VMThread`에 전달됩니다.

간단히 말해, **세이프포인트란 VM 내부의 모든 쓰레드가 정지된 상태**를 의미합니다. 또한, 네이티브 코드(native code)를 실행 중인 쓰레드는 세이프포인트가 진행되는 동안 **VM으로 다시 돌아오는 것이 차단**됩니다. 이 상태에서는 Java 힙을 수정 중인 쓰레드가 없고, 모든 쓰레드의 Java 스택이 **변하지 않는 상태**이므로, VM 작업을 안정적으로 실행할 수 있습니다.

가장 잘 알려진 VM 작업은 **가비지 컬렉션(GC)**, 특히 여러 GC 알고리즘에서 공통으로 사용되는 **"세상을 멈추는(stop-the-world)" 단계**입니다. 하지만 그 외에도 다양한 세이프포인트 기반 작업이 존재합니다. 예를 들면:

- **편향 락(biased locking)의 해제**
- **쓰레드 스택 덤프**
- **쓰레드 일시중지 또는 정지** (예: `java.lang.Thread.stop()` 호출)
- **JVMTI를 통해 요청되는 다양한 검사/수정 작업**

많은 VM 작업은 **동기적(synchronous)**입니다. 즉, 요청자는 해당 작업이 완료될 때까지 대기합니다. 하지만 일부는 **비동기적(asynchronous)**이거나 **병렬적(concurrent)**이며, 이런 경우에는 (세이프포인트가 시작되지 않은 이상) 요청자가 `VMThread`와 병렬로 계속 실행할 수 있습니다.

------

### 세이프포인트는 어떻게 시작되는가?

세이프포인트는 **협력적인(cooperative), 폴링 기반(polling-based)** 메커니즘을 통해 시작됩니다. 간단히 말해, 각 쓰레드는 주기적으로 “**세이프포인트 때문에 내가 멈춰야 하나?**”라는 질문을 스스로에게 던집니다.

이 질문을 효율적으로 던지는 것은 간단하지 않습니다.
 이 질문은 특히 **쓰레드 상태 전이(thread state transition)** 도중 자주 발생합니다. 단, 모든 상태 전이가 그런 것은 아니며, 예를 들어 VM을 떠나 네이티브 코드로 진입할 때는 질문하지 않습니다. 하지만 많은 경우에는 질문이 발생합니다.

그 외에도, **컴파일된 코드 내에서 메서드에서 반환할 때**, 또는 **루프 반복의 특정 지점**에서도 질문이 발생합니다.

**인터프리터(interpreter)**를 통해 실행되는 코드에서는 이러한 질문을 매번 코드에 넣는 대신, 세이프포인트 요청 시 **질문 코드를 포함하는 다른 디스패치 테이블로 전환**합니다. 세이프포인트가 종료되면 원래의 디스패치 테이블로 다시 전환됩니다.

------

### 세이프포인트 진행 방식

세이프포인트가 요청되면 `VMThread`는 모든 쓰레드가 세이프포인트에 **안전한 상태(safepoint-safe)**임을 확인할 때까지 기다립니다. 그런 다음에야 VM 작업을 실행할 수 있습니다.

세이프포인트 동안에는 `Threads_lock`을 사용해 실행 중인 모든 쓰레드를 차단합니다. 그리고 VM 작업이 완료되면 `VMThread`는 최종적으로 `Threads_lock`을 해제합니다.

- A 쓰레드가 새로 생성되어 리스트에 추가되려는 순간
- 동시에 GC가 실행 중이라 리스트를 순회하고 있을 수도 있죠
- 이때 **락 없이 동시 접근하면 데이터 손상 또는 충돌** 발생 가능

→ 그래서 `Threads_list`를 조작할 때는 반드시 `Threads_lock`을 획득해야 한다.
