# 10_BlockingQueue

> - 데이터 추가 차단 : 큐가 가득 차면 데이터 추가 작업을 시도하는 스레드는 공간이 생길 때 까지 차단
> - 데이터 획득 차단 : 큐가 비어 있으면 획득 작업을 시도하는 스레드는 큐에 데이터가 들어올때까지 차단

## BlockingQueue Implemet

- `ArrayBlockingQueue` : **배열 기반**으로 구현되어 있거, 버퍼의 크기가 고정되어 있다.
- `LinkedBlockingQueue` : **링크 기반**으로 구현되어 있고, 버퍼의 크기를 고정할 수도, 또는 무한하게 사용할 수도 있음

- BlockingDeque도 있음

```java
private BlockingQueue<String> queue;

public BoundedQueueV6_1(int max){
    this.queue = new ArrayBlockingQueue<>(max);
}

@Override
public void put(String data) throws InterruptedException {
    queue.put(data);
}

@Override
public String take() throws InterruptedException {
    return queue.take();
}

@Override
public String toString() {
    return queue.toString();
}
```





## BlockingQueue 기능

> - 멀티스레드를 사용할 때는 응답성이 중요하다.
>   - ex_대기 상태에 있어도, 고객이 중지 요청으로 하거나, 또는 너무 오래 대기한 경우 포기하고 빠져나갈 수 있는 방법이 필요

### 큐가 가득 찼을 때 생각할 수 있는 선택지 4가지

- 예외를 던진다. 예외를 받아서 처리
- 대기하지 않고, 즉시 false
- 대기 or 일정 시간만 대기



### Throws Exception - 대기시 예외

- **add(e)** : 지정된 요소를 큐에 추가, 큐가 가득차면 `IllefalStateException` 예외
- **remove()** : 요소 제거, 큐가 비어있으면 `NoSuchElementException` 예외
- **element()** : 큐의 머리 요소를 반환만 한다. (제거하지는 않음). 큐가 비어있으면 `NoSuchElementException` 예외



### Special Value - 대기 시 즉시 반환

- **offer(e)** : 추가 + 큐가 가득차면 `false` 반환
- **poll()** : 제거, 반환 + 큐가 비어있으면 `null` 반환
- **peek()** : 머리 요소 반환 + 큐가 `null` 반환

### 

### Blocks - 대기

- **put(e)** : 추가 + 대기
- **take()** : 제거 + 대기
- **Examine (관찰)** : 해당 사항 없음



### Times Out - 시간 대기

- **offer(e, time, unit)** : 추가 + 큐가 가득차고 시간 초과 `false` 반환
- **poll(time, unit)** : 제거, 반환 + 큐가 비어있고 시간 초과 `null` 반환
- **peek()** : 머리 요소 반환 + 큐가 `null` 반환





