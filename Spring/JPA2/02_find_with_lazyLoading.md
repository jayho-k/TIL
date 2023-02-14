# 02_lazyLoading

> - DTO추가
> - fetch join 추가
> - JPA에서 DTO직접 호출 (new를 사용해서)

- 등록이랑 수정은 보통 성능에 문제를 일으키지 않는다.
- 보통 최적화를 해야할 경우라면 조회에서 많이 터지게 된다.

```java
@Entity
@Table(name = "orders")
@Getter @Setter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Order {

    @Id @GeneratedValue
    @Column(name = "order_id")
    private Long id;

    @ManyToOne(fetch = LAZY)
    @JoinColumn(name = "member_id")
    private Member member;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
    private List<OrderItem> orderItems = new ArrayList<>();

    @OneToOne(fetch = LAZY, cascade = CascadeType.ALL)
    @JoinColumn(name = "delivery_id")
    private Delivery delivery;

    private LocalDateTime orderDate; //주문시간

    @Enumerated(EnumType.STRING)
    private OrderStatus status; //주문상태 [ORDER, CANCEL]
```

- Member와 Delivery의 경우 지연로딩으로 설정이 되어있다.
  - 따라서 실제 Entity가 아니라 프록시로 존재한다는 뜻

#### DTO 추가 But, N+1문제

- DTO를 추가하지 않을시 => 무한 루프에 빠질 수 있음
  - 이유 : Order에 가면 Member가 존재, Member에 가면 Order가 존재하기 떄문이다.
  - JsonIgnore를 해주면 되는데 DTO를 사용하는 것이 좋음

```java
@GetMapping("/api/v2/simple-orders")
public List<SimpleOrderDto> ordersV2() {
     List<Order> orders = orderRepository.findAll();
     List<SimpleOrderDto> result = orders.stream()
     	.map(o -> new SimpleOrderDto(o))
     	.collect(toList());
     return result;
}
```

- DTO를 추가한 식이다 SimpleOrderDto가 Type인 것을 알 수 있다.
- 여기서 문제점은 **Member와 Delivery의 경우 지연로딩**으로 설정되어 있다.
  - Order를 먼저 불러옴 => 그다음에 Member와 Delivery가 Entity로 있다든 것을 파악함
  - 다시 DB에 Member와 Delivery를 불러오게 된다.
- ==> 즉 객체가 존재한다고 생각할때 마다 DB에서 값을 호출하게 된다.
- ==> **N+1문제 발생**
  - Order조회 => sql1번 실행 => 주문수가 2개 존재 => 결과 주문수 2개 쿼리 날림


**주의**

- 지연로딩을 피하기 위해서 EAGER를 사용해선 안된다.
- **연관관계가 필요없는 경우에도 데이터를 항상 조회**해서 성능 문제가 있을 수 있다.



#### fetch join추가

**OrderSimpleApiController**

```java
@GetMapping("/api/v3/simple-orders")
public List<SimpleOrderDto> ordersV3() {
     List<Order> orders = orderRepository.findAllWithMemberDelivery();
     List<SimpleOrderDto> result = orders.stream()
             .map(o -> new SimpleOrderDto(o))
             .collect(toList());
	return result;
}
```

**OrderRepository - 추가 코드**

```java
public List<Order> findAllWithMemberDelivery() {
 return em.createQuery(
     	"select o from Order o" +
         " join fetch o.member m" +
         " join fetch o.delivery d", Order.class)
 .getResultList();
}
```

- Order를 조회 할 것인데 member와 delivery를 조인해서 같이 가지고 와달라는 뜻이다.
- 이렇게 되면 member, delivery가 **이미 조회된 상태로 되기때문에 지연로딩**이 아니게 된다.



#### JPA에서 DTO 바로 조회

**OrderSimpleApiController**

```java
private final OrderSimpleQueryRepository orderSimpleQueryRepository; //의존관계
/**
 * V4. JPA에서 DTO로 바로 조회
 * - 쿼리 1번 호출
 * - select 절에서 원하는 데이터만 선택해서 조회
 */
@GetMapping("/api/v4/simple-orders")
public List<OrderSimpleQueryDto> ordersV4() {
 	return orderSimpleQueryRepository.findOrderDtos();
}
```

**OrderSimpleQueryRepository 조회 전용 리포지토리**

```java
@Repository
@RequiredArgsConstructor
public class OrderSimpleQueryRepository {
     private final EntityManager em;
     public List<OrderSimpleQueryDto> findOrderDtos() {
     return em.createQuery(
     "select new jpabook.jpashop.repository.order.simplequery.OrderSimpleQueryDto(o.id, m.name, o.orderDate, o.status, d.address)" +
     " from Order o" +
     " join o.member m" +
     " join o.delivery d", OrderSimpleQueryDto.class)
 .getResultList();
 }
}
```

**OrderSimpleQueryDto 리포지토리에서 DTO 직접 조회**

```java
public OrderSimpleQueryDto(
    		Long orderId, String name, LocalDateTime 
			orderDate, OrderStatus orderStatus, Address address) 
{
         this.orderId = orderId;
         this.name = name;
         this.orderDate = orderDate;
         this.orderStatus = orderStatus;
         this.address = address;
 }
```

- 일반적인 SQL을 사용할 때 처럼 **원하는 값을 선택해서 조회**하면 된다.
- new 명령어를 사용해서 JPQL의 결과를 DTO로 즉시 변환
- SELELCT절에서 원하는 데이터를 직접 선택함 => 어플리케이션 네트워크 용량 최적화
- 단점
  - 리포지토리 재사용성이 떨어지게 된다.
  - 왜냐하면 fit한 값들이 들어가기 때문이다
    - 따라서 복잡한 쿼리가 나올 경우에는 따로 뽑아내서 디자인해주는 것이 좋다.

**권장 순서**

- DTO로 사용함
- 필요하면 fetch join으로 성능을 최적화 한다. ==> 대부분은 성능이슈가 해결된다.
- 안될 시 => DTO로 직접 조회하는 방법을 사용한다.
- 안될 시 => SQL직접 사용



















