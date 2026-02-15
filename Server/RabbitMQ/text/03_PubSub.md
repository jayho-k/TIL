# 03_PubSub

- Pub/Sub 은 메시지발행과 구독의 개념을 기반으로 하는 메시징 패턴이다.
- 메시지를 중간 브로커(Exchange)를 통해 구독자들에게 메시지를 전달한다.
- RabbitMQ에서는 Fanout Exchange를 통해 연결된 모든 Queue에게 메시지를 전달하므로 Binding 을 통해서 Exchange를 연결하여 동시에 메시지를 받을 수 있다.
  - Binding : Exchange와 Queue와의 관계를 정의한 일종의 라우팅 테이블



### Pub/Sub 모델 특징 

1. **다대다 메시징**
   - 하나의 메시지가 여러 Subscriber 에게 전달이 가능
   - 메시지 복사자 이뤄지기 때문에 동일한 메시지가 여러 큐에 처리 되므로 중복처리 로직이 필요할 수 있음
2. **구독자 독립성**
   - Publisher는 메시지가 어떤 Subscriber에게 전달될지 알 필요가 없음
   - 메시지의 전달은 브로커가 처리하게 된다
3. **비동기 메시징**
   - Publisher와 Subscriber는 서로 독립적으로 동작하며, 동시에 실행될 필요가 없음
4. **확장성**
   - 여러 Subscriber를 추가하거나 제거해도 시스템이 영향을 받지 않음
5. **구독 제어**
   - 구독자는 특정 조건(예: 라우팅 키, 토픽)을 기반으로 메시지를 필터링하여 수신할 수도 있다.
   - Fanout Exchange는 모든 구독자에게 메시지를 브로드캐스트하는 반면(Routing Key는 필요하지 않음), Topic Exchange나 Direct Exchange는 메시지를 선택적으로 전달 가능

















