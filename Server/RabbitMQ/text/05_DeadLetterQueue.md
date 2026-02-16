# 05_DeadLetterQueue

### DLQ 란

- 메시지가 큐가에서 제대로 처리 되지 못할 경우 DLQ에 이동 되며, 실패한 메시지를 저장하는 용도로 사용한다.

**DLQ 로 가는 경우**

- **NACK 처리나 거부된 경우**
  - basic.reject 혹은 basic.nack 으로 메시지가 처리되지 못한 경우
- **TTL 만료된 경우**
  - TTL 초과된 경우 DLQ로 이동하게 된다.
- **큐 설정 초과된 경우**
  - 큐에 설정된 최대 메시지 갯수를 초과하면 가장 오래된 메시지가 삭제되고 DLQ로 이동



### DLX (Dead Letter Exchange)

- 큐 실패시에 DLX 를 설정하여 메시지가 처리도지 못한 경우 지정된 큐로 이동시킬 수 있다.
- ex
  - 잘못된 형식의 큐로 인해서 처리가 어려운 경우 DLQ 영역으로 이동하여 에러의 원인을 분석 후 재 처리를 시도할 수 있다.
  - 이떄 DLX에 전달 되고, DLQ에 있는 메시지를 통해 에러의 원인을 분석할 수 있다.

```java
@Bean
public Queue orderQueue(){
    return QueueBuilder.durable(MAIN_QUEUE)
        .withArgument("x-dead-letter-exchange", DLX) // DLX
        .withArgument("x-dead-letter-routing-key", DLQ) // D
        .build();
}
```



### 구현

- SimpleRabbitListenerContainerFactory 의 수동 Ack 모드 설정 = (AcknowledgeMode.MANUAL)
- **channel.basicAck : **
  - **메시지가 성공적으로 처리 되었다는 것을 리턴**
  - 메시지가 Ack 되면 메시지를 큐에서 삭제하고 다른 소비자에게 전송하지 않음
- **종류**
  - `channel.basicAck(tag, false ); // Ack 전송`
    - deliveryTag(long) 필드는 메시지 고유식별 태그
    - multiple(boolean) 필드는 true 일 경우 이전의 모든 메시지를 한꺼번에 Ack 처리, false 일 경우 현재 태그의 메시지 하나만 Ack 처리
  - `channel.basicNack(tag, false , false ); // DLQ로 메시지 이동`
    - deliveryTag
    - multiple
    - requeue가 true 일 경우 메시지를 큐에 다시 넣어 재처리 하도록 설정, false 의 경우 메시지를 DLQ로 이동 또는 삭제
  - `channel.basicReject(deliveryTag, requeue);`
    - 파라미터 동일

**RabbitMQ의 저수준 API 를 명확하게 이해해야 세밀한 애플리케이션에 적용할 수 있다. 또한 Production에서는 유지보수가 어려워진다는 단점이 있다.**

\>> 따라서 `RetryTemplate`을 통해서 더 로직을 쉽게 관리하는 방법을 사용한다. 
(이부분은 어떤 게 유지보수가 어렵고 AUTO로 하면 문제가 무엇인지 확인을 해보고 결정해야할 것으로 보인다.)



## RetryTemplate

- `RetryTemplate` 
  - Spring AMQP 는 RetryTemplate을 통해 재시도 로직을 지원한다.
  - 최대 3번 재시도 진행한 뒤에 실패하면 Spring이 메시지를 DLQ로 이동하게 된다.
- `AcknowledgeMode.AUTO`
  - 재시도 중 메시지가 성공적으로 처리되면 Spring AMQP가 자동으로 Ack를 전송 
  - 모든 재시도가 실패하면 Nack를 보내고 RabbitMQ가 메시지를 DLQ로 이동 
  - DLQ에서 메시지를 수정한 뒤 원래 큐로 재전송하여 정상 처리









