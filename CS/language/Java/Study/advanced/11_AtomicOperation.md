# 11_AtomicOperation

> - 해당 연산이 더 이상 나눌 수 없는 단위로 수행된다는 것을 의미
> - 멀티스레드 상황에서 다른 스레드의 간섭 없이 안전하게 처리되는 연산이라는 뜻

```java
volatile cnt = 0;

cnt = 1; // 원자적 연산
cnt++; // 원자적 연산 X
cnt = cnt+1; // 원자적 연산 X
```



## 성능 비교

```
BasicInteger: ms = 38
VolatileInteger: ms = 143
SyncInteger: ms = 507
MyAtomicInteger: ms = 214 // AtomicInteger사용
```

- `BasicInteger`

  - 캐시를 사용해서 가장 빠르다

  - 멀티 스레드 상황에서는 사용할 수 없다.

  - 단일 스레드일 경우에 가장 효율적이다.

    

- `VolatileInteger`

  - 멀티스레드에서 사용할 수 없다.

  - volatile은 메모리 가시성에 대한 해결방안이지 동시성 문제를 해결하기 위한게 아니다.

  - 원자적 연산일 때 사용가능 : ex) flag = false

    

- `SyncInteger`

  - 멀티스레드 환경에서 사용가능하다.

  - MyAtomicInteger 보다 성능이 느리다.

    

- `MyAtomicInteger `

  - lock을 사용하는 방법 보다 1.5~2배정도 빠르다.
  - 내부에 lock을 사용하지 않기 떄문이다.



## CAS(Compare-And-Swap) 연산 1

- **락 방식의 문제점**
  - 락을 획득하기 까지 일련의 과정이 필요하다. 
    1. 락이 있는지 확인
    2. 락을 획득하고 임계영역에 들어감
    3. 작업 수행
    4. 락을 반납
- **특별한 경우에 CAS를 적용시킬 수 있다.**



### CAS 는 원자적 연산이다??

<img src="./11_AtomicOperation.assets/image-20250120224958840.png" alt="image-20250120224958840" style="zoom:67%;" />

```
CPU가 원자적 연산으로 처리한다. [하드웨어 차원에서 지원]
1. x001의 값을 확인
2. 읽은 값이 0이면 1로 변경한다.

위 두 과정을 CPU에서 하나의 원자적 명령으로 만들어버린다 ==> 다른 스레드가 중간에 개입할 수 없음

- CPU에게 성능적 영향이 끼치지 않는다.

```

- 



## CAS(Compare-And-Swap) 연산 2

- `incrementAndGet` 구현해보기
- `compareAndSet` : **어느 쓰레드도 값을 바꾸지 않았을 경우에만 값을 바꾸겠다는 뜻이다.**
  - `atomicInteger.compareAndSet(getValue, getValue + 1);`
  - getValue값이 1이라면 True => 1+1 =2 로 바꾸겠다.
  - 내가 읽은 값이 변경이 안됐을 경우에만 바꾼다.

```java
    private static int incrementAndGet(AtomicInteger atomicInteger) {
        int getValue;
        boolean result;

        do{
            getValue = atomicInteger.get(); // thread1 : 0
            log("getValue : " + getValue);

            // 중간에 thread2 : value->1로 이미 만든 상태?
            // compareAndSet 부분에서 False가 나올 것임
            // 그럼 while문을 다시 돌린다. => 즉 최신 업데이트 부터 보는 것

            // 아무도 바꾸지 않았을 경우에만 값을 바꾸겠다는 뜻이다.
            result = atomicInteger.compareAndSet(getValue, getValue + 1);
            log("result : " + result);
        }while (!result);

        return getValue;
    }
```



- **Main**
  - Thread 2개를 만들어서 돌려보자!

```java
public static void main(String[] args) throws InterruptedException {
    AtomicInteger atomicInteger = new AtomicInteger(0);
    System.out.println("start value = " + atomicInteger.get());

    Runnable runnable = new Runnable() {
        @Override
        public void run() {
            incrementAndGet(atomicInteger);
        }
    };
	
    // Thread 생성 / THREAD_COUND = 2
    List<Thread> threadList = new ArrayList<>();
    for (int i = 0; i < THREAD_COUND; i++){
        Thread thread = new Thread(runnable);
        threadList.add(thread);
        thread.start();
    }

    for (Thread thread : threadList){
        thread.join();
    }

    int res = atomicInteger.get();
    System.out.println(res);
}
```

- 실행결과
  - Thread - 1 이 false로 실패하고 다시 시도하는 것을 볼 수 있다.

```java
start value = 0
21:16:19.304 [ Thread-0] getValue : 0 
21:16:19.304 [ Thread-1] getValue : 0 
21:16:19.307 [ Thread-1] result : false // 첫번째 시도 = 실패
21:16:19.307 [ Thread-0] result : true
21:16:19.408 [ Thread-1] getValue : 1 
21:16:19.408 [ Thread-1] result : true // 두번쨰 시도 후 성공
AtomicInteger resultValue : 2
```

- 실행 과정
  - thread 0 : 0 에서 1로 update
  - thread 1 : 0 에서 1로 update를 하려했으나 이미 업데이트가 되어있음
    - 즉  compareAndSet 부분에서 False가 나옴
  - thread 1 : 다시 get으로 읽고(1) update 시도(2) 후 완료



### CAS 의 단점

- **충돌이 빈번하게 발생하는 환경에서 성능에 문제가 될 수 있음**
  - CAS가 자주 실패하고 재시도를 할 것이기 때문
  - 결과적으로 CPU 자원을 많이 소모하게 된다.
    - Lock일 경우 : wait로 재우기 때문에 CPU 자원 소모가 덜 함



### CAS와 Lock 비교

- **`Lock`**
  - 비관적 접근법
  - 다른 스레드의 접근을 막음
  - 즉 **"다른 스레드가 방해할 것을 전제"**로 사용
- **`CAS`**
  - 낙관적 접근법
  - 락을 사용하지 않고 데이터에 바로 접근
  - **"충돌이 별로 없을 것을 전제로 "** 사용



### CAS 방식을 사용할 때

- 간단한 연산일 때 사용하는 것이 좋음



## CAS Lock 구현

```java
public static void main(String[] args) {
    //SpinLockBad spinLock = new SpinLockBad();
    SpinLock spinLock = new SpinLock();

    Runnable runnable = new Runnable() {
        @Override
        public void run() {
            spinLock.lock();
            // critical section
            try {
                log("비즈니스 로직 실행");
                sleep(1); // 비즈니스 로직이 1ms 걸린다고 가정
            } finally {
                spinLock.unlock();
            }
        }
    };

    Thread t1 = new Thread(runnable, "Thread-1");
    Thread t2 = new Thread(runnable, "Thread-2");

    t1.start();
    t2.start();
}
```

```java
public class SpinLock {

    private final AtomicBoolean lock = new AtomicBoolean(false);

    public void lock(){
        log("lock acquired");
        while (!lock.compareAndSet(false, true)){
            log("lock 획득 실패 - 스핀 대기");
        }
        log("lock 획득 성공");
    }

    public void unlock(){
        lock.set(false);
        log("lock return complete");
    }

}
```

- sleep(1); // 비즈니스 로직이 1ms 걸린다고 가정 = 결과

```
 09:41:04.925 [ Thread-1] 락 획득 시도
09:41:04.925 [ Thread-2] 락 획득 시도
09:41:04.927 [ Thread-1] 락 획득 완료
09:41:04.927 [ Thread-1] 비즈니스 로직 실행
09:41:04.927 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.927 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.927 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.927 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.927 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.927 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.927 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.927 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.927 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-2] 락 획득 실패 - 스핀 대기
09:41:04.928 [ Thread-1] 락 반납 완료
09:41:04.928 [ Thread-2] 락 획득 완료
09:41:04.929 [ Thread-2] 비즈니스 로직 실행
09:41:04.930 [ Thread-2] 락 반납 완료
```

- 락 획득 시도를 계속 하고 있다. (spin lock)

  

### CAS Lock 을 사용해야 할 때

- 안전한 임계 영역이 필요하지만, **연산이 길지 않고 매우 짧게 끝날 때 사용해야한다.  (1ms 이하일 때 주로 사용)**
- 예를 들어 숫자 값의 증가, 자료구조의 데이터 추가 등
- 사용하면 안되는 경우 = DB 결과값 대기, 다른 서버의 요청 등



## 실무

- 실무 관점에서 대부분의 애플리케이션들은 공유자원을 사용할 때, 충돌핳지 않을 가능성이 훨씬 높다.

```
피크시간 주문 100만건 
주문 수를 실시간으로 증가하면서 카운트 한다고 가정 = 단순 연산
- 1,000,000 / 60분 = 1분 : 16,666건, 1초 : 277건
- 1초에 277건이면 CAS 처럼 낙관적인 방식이 더 나은 성능을 보인다.
```

- CAS 연산을 직접 사용하는 경우는 드물다. 라이브러리, 동기화 컬렉션을 잘 이해하고 사용할 줄 알면 된다.















