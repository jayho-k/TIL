# 05_Interrupt



## Interrupt?

- waiting, timed_wating 같은 대기 상태의 스레드를 직접 깨워서, 작동하는 runnable 상태로 변경할 수 있음

```java
public static void main(String[] args) {
    MyTask myTask = new MyTask();
    Thread thread = new Thread(myTask);
    thread.start();

    sleep(4000);

    log("중단 지시 : thread.interrupt();");
    thread.interrupt();
    log("interrupt 상태 1 : " + thread.isInterrupted());
}
static class MyTask implements Runnable {

    @Override
    public void run() {
        try {
            while(true){
                log("시작");
                Thread.sleep(3000);
                log("끝");
            }
        }
        catch (InterruptedException e) {
            log("interrupt 상태 2 : " + Thread.currentThread().isInterrupted());
            log(e.getMessage());
            log("thread 상태 : " + Thread.currentThread().getState());
        }
    }
}
```

- 순서
  1. thread start
  2. run 작업 3초
  3. run 작업 1초 => main thread 가 interrupt
  4. 인터럽트 작동됨
     
- Interrupt 거는 타이밍이 언제인가?
  - Thread.sleep(3000); 이때 상태가 sleep 상태일 때 깨우는 것이다. 	
    => RUNNABLE 상태로 만듦
  - 즉 Thread.sleep(3000); 가 들어가 있는 동안 interrupt를 사용하면 interrupt가 발동된다.
    => 



### + 꼭 Sleep 에서만 interrupt 발생을 해야하는 것인가

```java
while(true){ // ==> 여기서 발생시키면 더 좋지 않은가?
    log("시작");
    Thread.sleep(3000); // 여기서만 interrupt 발생
    log("끝");
}
```

- 변경 코드

```java
public static void main(String[] args) {

    MyTask myTask = new MyTask();
    Thread thread = new Thread(myTask);
    thread.start();

    sleep(20);

    log("중단 지시 : thread.interrupt();");
    thread.interrupt();
    log("interrupt 상태 1 : " + thread.isInterrupted()); // interrupt 상태 : true
}


static class MyTask implements Runnable{

    @Override
    public void run() {
        while(!Thread.interrupted()){ // !Thread.currentThread().isInterrupted()) ??
            log("시작");
        }
		// interrupt 상태 : false
        try {
            log("자원 정리 시작");
            Thread.sleep(1000);
            log("interrupt 상태 3 : " + Thread.currentThread().isInterrupted());
            log("자원 정리 종료");
        } catch (InterruptedException e) {
            log("interrupt 상태 4 : " + Thread.currentThread().isInterrupted());
        }
    }
}
```

- 주의
  - `!Thread.currentThread().isInterrupted())` 를 사용하면 **자원 정리 할때도Thread.sleep(1000); 에서 예외를 터트려서 죽는다.**
    - 이유 : isInterrupted를 사용하면 **interrupt 를 true 상태로 유지 하기 때문이다.**
- 자원정리까지 완료하고 끄고 싶다면? 
  - interrupt를 true에서 false(정상상태로) 다시 변경하는 기능이 필요
  - => `!Thread.interrupted()`  : 이 함수가 true로 변환 시키고 다시 false(정상상태)로 변경하는 기능을 한다.
  - 따라서 while(!Thread.interrupted()) 여기서 true로 변환시켜 진행을 interrupt 작동을 시키고 false로 변환되면서 자원 정리 로직을 수행 할 수 있다.



**예제**

```java
public static void main(String[] args) {

    Printer printer = new Printer();
    Thread printerThread = new Thread(printer, "printer");
    printerThread.start();

    Scanner userInput = new Scanner(System.in);

    while (true){
        log("프린터할 문서를 입력하세요. 종료 (q): ");
        String input = userInput.nextLine();
        if(input.equals("q")){
            printerThread.interrupt();
            break;
        }
        printer.addJob(input);
    }

}

static class Printer implements Runnable {

    volatile boolean work = true; // 여러 스레드가 동시에 접근하는 변수에는 volatile 키워드를 붙여줘야 안전
    Queue<String> jobQueue = new ConcurrentLinkedQueue<>(); // 동시성 컬렉션을 사용해야한다.

    @Override
    public void run() {
        while(!Thread.interrupted()){
            if (jobQueue.isEmpty())
                continue;
            try {
                String job = jobQueue.poll();
                log("출력 시작 : " + job + ", 대기 문서: " + jobQueue);
                Thread.sleep(3000);
                log("출력 종료");
            } catch (InterruptedException e) {
                log("interrupt!");
                break;
            }
        }
        log("printer 종료");
    }

    public void addJob(String input){
        jobQueue.offer(input);
    }
}
```



## yield - 양보하기

> - CPU 실행 기회를 양보하고 싶을 수 있음
> - 이렇게 양보하면 스케줄링 큐에 대기 중인 다른 스레드가 CPU 실행 기회를 더 빨리 얻을 수 있음

```java
static final int THREAD_COUNT = 1000;

public static void main(String[] args) {
    for (int i = 0; i < THREAD_COUNT; i++){
        Thread thread = new Thread(new MyRunnable());
        thread.start();
    }
}


static class MyRunnable implements Runnable{

    @Override
    public void run() {
        for(int i = 0; i<10; i++){
            System.out.println(Thread.currentThread().getName() + " - " + i);
            //  x : 1번 방법 => 한 스레드가 계속 많이 실행되는 모습을 보임
            //sleep(1); // 2번 방법 => 실행 스케줄링에서 잠시 제외 된다. (TIME_WAITING -> RUNNABLE)
            Thread.yield(); // 3번 방법 => thread의 상태는 동일(runnable) 하지만 대기열애 들어가는 상황
        }
    }
}
```

- runnable을 두가지 상태가 있음
  1. 작업 중인 상태
  2. 작업을 하기 위해 대기열에 준비 중인 상태
- **sleep**
  -  실행 스케줄링에서 잠시 제외 된다. (TIME_WAITING -> RUNNABLE)
  - RUNNABLE => TIMED_WAITING => RUNNABLE : 복잡
  - 특정 시간만큼 스레드가 실행되지 않는 단점이 있다.
  - 양보할 사람이 없는데 혼자 양보하는 상황이 나올 수 있다.
- **yield**
  - **thread의 상태는 동일(runnable) 하지만 대기열애 들어가는 상황**
  - 운영체제 입장에서 read로 만든 것이라고 보면 된다.
    - 운영체제에 단지 hint를 주는 것 뿐 반드시 다른 스레드에게 양보하게 만드는 것이 아니다.
    - 즉 **양보할 사람이 없다면 본인 스레드가 계속 실행한다.**

```java
static class Printer implements Runnable {
    
    Queue<String> jobQueue = new ConcurrentLinkedQueue<>(); 

    @Override
    public void run() {
        while(work){
            if (jobQueue.isEmpty()){
                Thread.yield(); // 이 부분이 바뀜 / 아래 설명
            }
            String job = jobQueue.poll();
            log("출력 시작 : " + job + ", 대기 문서: " + jobQueue);
            sleep(3000);
            log("출력 종료");
        }
    }
}
```

- 기존 코드 : continue
- 변경 코드 : Thread.yield();
- 기존 코드일 경우 CPU의 자원을 계속 먹고 있음 
  => 따라서 다른 스레드에게 양보함으로써 CPU 자원을 효율 적으로 사용하게 하기 위함















