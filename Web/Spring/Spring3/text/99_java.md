# 99_java

## `Thread.sleep()`과 `InterruptedException`

```java
public static void sleep(long millis) {
  try {
    Thread.sleep(millis);
  } catch (InterruptedException ex) {
	// ...
  }
```

```java
while (!Thread.currentThread().isInterrupted()) {
  try {
    // Thread.sleep(), Future.get(),
    // BlockingQueue.take() 등이 여기올 수 있다.
  } catch (InterruptedException ex) {
    Thread.currentThread().interrupt();
  }
}
```

- `InterruptedException`
  - thread에 하던일을 멈추라는 신호를 보내기 위해 인터럽트를 사용한다.
- 인터럽트
  - 스레드를 종료하기 위한 메커니즘
  - 