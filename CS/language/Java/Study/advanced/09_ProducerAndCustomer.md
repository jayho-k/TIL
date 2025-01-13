# 09_ProducerAndCustomer



## basic 

- **생산자**

  - 데이터를 생성하는 역할

  - ex_ 파일 read, network 데이터 등

    

- **소비자**

  - 생성된 데이터를 사용하는 역할

  - ex_ 데이터 처리, 저장

    

- **버퍼**

  - 생산자가 생성한 데이터를 일시적으로 저장하는 공간
  - 한정된 크기
  - 생산자와 소비자가 이 버퍼를 통해 주고 받음

- 문제 상황

  - **생산자가 너무 빠를 때**

    - 버퍼가 가득 차서 더 이상 데이터를 넣을 수 없을 때까지 생산자가 데이터를 생성

    - 버퍼가 가득 찬 경우 **생산자는 버퍼에 빈 공간이 생길 때까지 기다려야 한다**.

      

  - **소비자가 너무 빠를 때**

    - 버퍼가 비어서 더 이상 소비할 데이터가 없을 떄까지 소비자가 데이터를 처리
    - 버퍼가 비어있을 때 **소비자는 새로운 데이터가 들어올 떄까지 기다려야한다.**



**임계 영역**

- 핵심 공유 자원 : queue(ArrayDeque)
- `synchronized`  를 사용해서 한 번에 하나의 스레드만 put() 또는 take()를 할 수 있도록 설계

```java
// BoundedQueueV1
public class BoundedQueueV1 implements BoundedQueue{

    private final Queue<String> queue = new ArrayDeque<>();
    public final int max;

    public BoundedQueueV1(int max) {
        this.max = max;
    }

    @Override
    public synchronized void put(String data) {
        if (queue.size() == max){
            log("[put] 큐가 가득 참, 버림 : " + data);
        }
        queue.offer(data);
    }

    @Override
    public synchronized String take() {
        if(queue.isEmpty()){
            return null;
        }
        return queue.poll();
    }

    @Override
    public String toString() {
        return queue.toString();
    }
}

// ConsumerTask
@Override
public void run() {
    log("[소비 시도] ?  <-  " + queue);
    String data = queue.take();
    log("[소비 시도] ? "+ data + " <-  " + queue);
}

// ProducerTask
@Override
public void run() {
    log("[생산 시도] " + request + " -> " + queue);
    queue.put(request);
    log("[생산 완료] " + request + " -> " + queue);
}


// main
public static void main(String[] args) {

    BoundedQueue queue = new BoundedQueueV1(2);

    //producerFirst(queue);
    consumerFirst(queue);

}

private static void consumerFirst(BoundedQueue queue) {
    log("== [소비자 먼저 실행] 시작, "+ queue.getClass().getSimpleName() + "==");
    ArrayList<Thread> threads = new ArrayList<>();
    startConsumer(queue, threads);
    printAllState(queue, threads);
    startProducer(queue, threads);
    printAllState(queue, threads);
    log("== [소비자 먼저 실행] 종료, "+ queue.getClass().getSimpleName() + "==");
}

private static void producerFirst(BoundedQueue queue){
    log("== [생산자 먼저 실행] 시작, "+ queue.getClass().getSimpleName() + "==");
    ArrayList<Thread> threads = new ArrayList<>();
    startProducer(queue, threads);
    printAllState(queue, threads);
    startConsumer(queue, threads);
    printAllState(queue, threads);
    log("== [생산자 먼저 실행] 종료, "+ queue.getClass().getSimpleName() + "==");

}

private static void startConsumer(BoundedQueue queue, ArrayList<Thread> threads) {

    System.out.println();

    log("소비자 시작");
    for (int i =0; i<=3; i++){
        Thread consumer = new Thread(new ConsumerTask(queue), "consumer" + i);
        threads.add(consumer);
        consumer.start();
        sleep(100);
    }
}

private static void printAllState(BoundedQueue queue, ArrayList<Thread> threads) {

    System.out.println();
    log("현재 상태 출력, Q 데이터 : " + queue);
    for (Thread thread : threads){
        log(thread.getName() + ": " + thread.getState());
    }
}

private static void startProducer(BoundedQueue queue, ArrayList<Thread> threads) {
    System.out.println();
    log("생산자 시작");
    for (int i = 0; i< 3; i++){
        Thread producer = new Thread(new ProducerTask(queue, "data" + i), "producer"+i);
        threads.add(producer);
        producer.start();
        sleep(100);
    }
}

```

```
00:33:03.520 [     main] == [소비자 먼저 실행] 시작, BoundedQueueV1==

00:33:03.523 [     main] 소비자 시작
00:33:03.527 [consumer0] [소비 시도] ?  <-  []
00:33:03.531 [consumer0] [소비 시도] ? null <-  []
00:33:03.636 [consumer1] [소비 시도] ?  <-  []
00:33:03.636 [consumer1] [소비 시도] ? null <-  []
00:33:03.745 [consumer2] [소비 시도] ?  <-  []
00:33:03.745 [consumer2] [소비 시도] ? null <-  []
00:33:03.855 [consumer3] [소비 시도] ?  <-  []
00:33:03.855 [consumer3] [소비 시도] ? null <-  []

00:33:03.965 [     main] 현재 상태 출력, Q 데이터 : []
00:33:03.966 [     main] consumer0: TERMINATED
00:33:03.966 [     main] consumer1: TERMINATED
00:33:03.966 [     main] consumer2: TERMINATED
00:33:03.968 [     main] consumer3: TERMINATED

00:33:03.968 [     main] 생산자 시작
00:33:03.969 [producer0] [생산 시도] data0 -> []
00:33:03.970 [producer0] [생산 완료] data0 -> [data0]
00:33:04.075 [producer1] [생산 시도] data1 -> [data0]
00:33:04.075 [producer1] [생산 완료] data1 -> [data0, data1]
00:33:04.183 [producer2] [생산 시도] data2 -> [data0, data1]
00:33:04.185 [producer2] [put] 큐가 가득 참, 버림 : data2
00:33:04.185 [producer2] [생산 완료] data2 -> [data0, data1, data2]

00:33:04.291 [     main] 현재 상태 출력, Q 데이터 : [data0, data1, data2]
00:33:04.291 [     main] consumer0: TERMINATED
00:33:04.291 [     main] consumer1: TERMINATED
00:33:04.292 [     main] consumer2: TERMINATED
00:33:04.292 [     main] consumer3: TERMINATED
00:33:04.292 [     main] producer0: TERMINATED
00:33:04.292 [     main] producer1: TERMINATED
00:33:04.292 [     main] producer2: TERMINATED
00:33:04.293 [     main] == [소비자 먼저 실행] 종료, BoundedQueueV1==

Process finished with exit code 0
```

- 결국 결론은 데이터가 버려지게 된다는 것이다.
  - 생산자가 먼저 시작하든 소비자가 먼저 시작하든 기다리다가 받으면 된다.
- 이 데이터들을 기다리다가 깨어나서 큐에 들어가거나 받는 방법은 없을까?
- 코드를 수정해보자









