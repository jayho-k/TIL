# 01_RabbitMQ

## AMQP

Advances Message Queing Protoal




## 01. 용어 정리

1. **Producer (생산자):**
  메시지를 생성하고 RabbitMQ에 전송하는 애플리케이션
  Producer는 특정 Exchange에 메시지를 전송하고 Exchange는 메시지를 라우팅하
  여 큐에 배치
2. **Exchange :**
  - Producer로 부터 받은 메시지를 큐에 전달
    Exchange 유형:
    Direct: 특정 라우팅 키와 정확히 일치하는 큐에 메시지를 전송
    Fanout: 모든 큐에 메시지를 브로드캐스트
    Topic: 라우팅 키 패턴을 기반으로 메시지를 특정 큐에 전달
    Headers: 메시지 헤더 속성에 따라 메시지를 라우팅
    메시지가 Exchange로 전송될 때, Routing Key가 함께 전달
3. **Routing Key :**
  메시지를 전송할 때 Producer가 Exchange에 전달하는 키
  Exchange는 이 Routing Key를 참고하여 어떤 큐에 메시지를 전달할지 결정
4. **Queue :**
  메시지를 일시적으로 저장하는 버퍼 역할
  RabbitMQ의 큐는 FIFO(First In, First Out) 방식으로 동작하며, 메시지가 소비자에
  게 전달될 때까지 보관
  각 큐는 여러 Consumer가 구독(수신)할 수 있으며, 메시지는 큐에 들어온 순서대로
  전달
  비동기적으로 동작하며, 여러 컨슈머가 동시에 메시지를 소비할 수 있다. 단 하나의 메
  시지가 여러 소비자에게 중복으로 전달될수는 없음
  동일한 메시지를 수신하려면 Fanout Exchange 방식으로 동작해야만 함.



## vhost

- 권한 관리라고 생각하면 된다.
- 리소스들을 격리를 시키는 것이다.
- 따라서 각 어플리케이션이 vHost단위로 특정한 vHost로 접근할 수 있다.
- 





















