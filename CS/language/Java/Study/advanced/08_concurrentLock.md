# 08_concurrentLock

- synchronized의 무한 대기 현상을 막기 위한 기능들



## LockSupport 기능

> - LockSupport 는 스레드를 **WATING** 상태로 변경한다.
> - WATING 상태는 누가 꺠워주기 전까지는 계속 대기. 하지만 CPU 실행 스케줄링에 들어가지 않는다

### LockSupport 의 대표적인 기능

- **park()**
  - 스레드를 WAITING 상태로 변경
- **parkNanos(nano)**
  - 스레드를 나노초 동안만 TIMED_WAITING 상태로 변경한다.
  - 지정한 나노초가 지나면 RUNNABLE 상태로 변경된다.
- **unpark(thread)**
  - WAITING 상태의 대상 스레드를 RUNNABLE 상태로 변경한다.



### park, unpark

 ```java
 public static void main(String[] args) {
     Thread thread1 = new Thread(new ParkTest(), "Thread 1");
     thread1.start();
     sleep(100);
     
     log("Thread 1 state : " + thread1.getState());
     log("main -> unpark");
     
     LockSupport.unpark(thread1); // 1. unpark 사용 => interrupt 상태 : false 로 종료
     //thread1.interrupt(); // 2. interrupt() 사용 => interrupt 상태 : true 로 종료
 }
 
 static class ParkTest implements Runnable{
 
     @Override
     public void run() {
         log("park 시작");
         LockSupport.park();
         log("park 종료, state : " + Thread.currentThread().getState());
         log("interrupt 상태 : " + Thread.currentThread().isInterrupted());
     }
 }
 ```

- 각각의 스레드에서 park () => waiting
- main에서 원하는 스레드를 unpark() 시키면 => runnable로 변한
- unpark 와 interrupt 의 차이점
  - **unpark 사용 => interrupt 상태 : false 로 종료(정상)**
  - **interrupt() 사용 => interrupt 상태 : true 로 종료** 이므로 false로 바꿔줘야함





### parkNanos

```java
LockSupport.parkNanos(2000_000000); // parkNanos 2초
```

```
21:06:57.789 [ Thread 1] park 시작
21:06:57.889 [     main] Thread 1 state : TIMED_WAITING
21:06:59.802 [ Thread 1] park 종료, state : RUNNABLE
21:06:59.806 [ Thread 1] interrupt 상태 : false
```



### BLOCKED vs WAITING

- BLOCKED : 무한 대기 가능성 있음
  - 이유 : interrupt와 같은 기능으로 깨울 수 없기 때문이다. 즉 lock을 얻을 때 까지 무한 대기
- WAITING :  
  - interrupt로 깨울 수 있는 상태이기 때문에 무한대기 현상을 막아줄 수 있음











