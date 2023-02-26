# 03_collection

> ManyToOne => select
>
> - fetch join
> - paging

 상황 : 

- Order를 기준으로 OrderItem과 Item이 필요한 상황
- OneToMany의 값들도 불러오고 싶다는 뜻
  - Join을 해야할 경우에는 엔티티를 포함하고 있는 경우에만 해당된다.


**Order Entity**

```java
@Entity
@Table(name="orders")
@Getter @Setter
public class Order {

    @Id @GeneratedValue
    @Column(name = "order_id")
    private Long id;

    @ManyToOne(fetch = LAZY)
    @JoinColumn(name = "member_id")
    private Member member;

    private LocalDateTime orderDate;
    @Enumerated(EnumType.STRING)
    private OrderStatus status;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL) 
    private List<OrderItem> orderItems = new ArrayList<>();

    @OneToOne(fetch = LAZY, cascade = CascadeType.ALL) 
    @JoinColumn(name="delivery_id")
    private Delivery delivery;
}

```

- 즉 order items를 어떻게 처리할 것인가에 대한 이야기



## +DTO

**Controller**

```java
@GetMapping("/api/v2/orders")
public List<OrderDto> ordersV2() {
     List<Order> orders = orderRepository.findAll();
     List<OrderDto> result = orders.stream()
     .map(o -> new OrderDto(o))
     .collect(toList());
 return result;
}
```

**DTO**

```java
@Data // 대부분 프로퍼티 에러가 터지면 getter setter문제다
    static class OrderDto{

        private Long orderId;
        private String name;
        private LocalDateTime orderDate;
        private OrderStatus orderStatus;
        private Address address;
        private List<OrderItemDto> orderItems;

        public OrderDto(Order order) {
            orderId = order.getId();
            name = order.getMember().getName(); // member lazy초기화 시점
            orderDate = order.getOrderDate();
            orderStatus = order.getStatus();
            address = order.getDelivery().getAddress(); // lazy초기화 시점
            // V2에서 주의할 곳 
            // orderItems = order.getOrderItems();
            //order.getOrderItems().stream().forEach(o->o.getItem().getName()); 
            orderItems = order.getOrderItems().stream()
                    .map(orderItem-> new OrderItemDto(orderItem))
                    .collect(Collectors.toList());
        }
    }
```

- 컬렉션에서 주의할 점은 OrderItem같은 경우도 하나하나 객체이다
  - 즉 Order Item도 Dto를 따로 만들어주어야 한다는 뜻이다.

```java
// Order item Dto
@Data
static class OrderItemDto{
    private String itemName;
    private int orderPrice;
    private int count;
    public OrderItemDto(OrderItem orderItem){
        itemName = orderItem.getItem().getName();
        orderPrice = orderItem.getItem().getPrice();
        count = orderItem.getCount();
    }
}
```

-  Dto안에 Entity가 존재하면 안된다. => 엔티티를 노출 시키는 것과 똑같은 상황이다.
- Dto를 사용한다는 것은 단순히 Dto를 감싸서 보내라는 뜻이 아니다.
- Dto를 사용한다는 뜻은 **Entity와의 의존을 완전히 끊어버리는 것을 말하는 것이다.**
- 따라서 OrderItem조차 Dto로 변환시켜야한다.

**DTO만 추가했을 때 문제점**

- 지연로딩으로 너무 많은 SQLL이 실행된다.
  - **최악의 경우** : 이유 => 1차 캐싱때문
  - order 1번
  - member, address N번(order 조회 수 만큼)
  - orderItem N번(order 조회수 만큼)
  - item N번 (orderItem조회수 만큼)



## fetch join 추가 작업

```java
    public List<Order> findAllWithItem() {
        return em.createQuery(
                "select distinct o from Order o" +
                        " join fetch o.member m" +
                        " join fetch o.delivery d" +
                        " join fetch o.orderItems oi" +
                        " join fetch oi.item i", Order.class
        ).getResultList();
    }
```

- 이런식으로 사용하게 되면 하나하나 다 조인해서 가져오게 된다.

- 조인은 order id를 가지고 join을 하게 된다. 

  - 따라서 id4번을 가지고 있는 order item이 두개( 책 2권을 샀기 때문에 )이기 때문에 **하나만 나와도 되는 컬럼이 2개가 생성되어버린다.**
  - 즉 Join의 기준 N에 맞춰져 있다. => N개의 컬럼이 생겨서 반환이 되게 된다.
  - 즉 **데이터가 2배로 되어버려서 가져오게 된다.**

- **해결**

  - **distinct를 사용** =>  Order id가 같으면 중복이라고 생각하고 합쳐준다.
    참고 : SQL같은 경우의 distinct는 완전히 같아야 중복을 제거해준다는 다른점이 있다.

  - **문제점**

    - **페이징 불가능**

    - 왜냐하면 하이버네이트는 **메모리에서 페이징을 해버리기 때문**이다.

    - ex) 데이터가 10000개가 있다고 한다면 10000개를 application 다 퍼 올린 뒤에

      ​	  10000개를 다 메모리안에서 해결하려고 할 것이다.

      ​	  그렇다면 out of memory가 날 수 있음

**그럼 어떻게 해야하나?**

- ToOne => 모두 fetch join을 사용
- **collection은 지연로딩으로 조회**한다.

**주의**

- **컬렉션 fetch join은 하나만 써야한다** => 데이터가 부적합하게 조회될 수 있다.



## + Paging을 사용하는 방법

```
# 최적화 => 이 뜻은 in 쿼리의 개수를 한번에 얼마나 떙겨올것인가를 나타내는 옵견이다
# 그럼 사이즈는 얼마나 잡아야 하나?
# max는 1000개로 잡는 것이 좋다. 왜냐하면 DB에서 오류를 일으킬 수 있기 때문이다.
# 1000으로 한번에 잡으면 DB에 순간 부하가 증가할 수 있다.
# DB가 순간 부하를 어디까지 견딜 수 있는지로 결정하면 된다.
```

- ToOne관계는 모두 페치조인을 한다.
  - row수를 증가시키지 않기에 페이징 쿼리에 영향을 주지 않음
- 지연 로딩 성능 최적화를 위해 **hibernate.default_batch_fetch_size , @BatchSize** 를 적용한다.
  - 컬렉션이나, **프록시 객체를 한번에 IN쿼리로 조회**한다.
  - in 쿼리의 개수를 한번에 얼마나 떙겨올것인가를 나타내는 옵견이다

- **장점**
  - **쿼리 호출 수 N+1 => 1+1**
  - 페치 조인 방식과 비교해서 쿼리 호출 수가 약간 증가하지만, DB 데이터 전송량이 감소한다.

- **사이즈를 얼마나 잡아야하는가?**
  - **max는 1000개로 잡는 것이 좋다.** 왜냐하면 DB에서 오류를 일으킬 수 있기 때문이다.
  - 1000으로 한번에 잡으면 **DB에 순간 부하가 증가할 수 있다.**
  - DB가 순간 부하를 어디까지 견딜 수 있는지로 결정하면 된다.
  - 100~1000으로 설정



## JPA에서 DTO직접 조회 => 컬렉션 조회 최적화

**OrderApiController**

```java
@GetMapping("/api/v5/orders")
    public List<OrderQueryDto> ordersV5(){
        return orderQueryRepository.findAllByDto_optimizer();
    }

```

**OrderQueryRepository**

```java
public List<OrderQueryDto> findAllByDto_optimizer() {

        // findOrders로 member랑 delivery join해서 다 가져온다.
        List<OrderQueryDto> result = findOrders();

        // id값만 다 뽑아옴
        List<Long> orderIds = toOrderIds(result);

        // 필요한 값만 넣어서 item join하고
        Map<Long, List<OrderItemQueryDto>> orderItemMap = findOrderItemMap(orderIds);
        //
        result.forEach(o-> o.setOrderItems(orderItemMap.get(o.getOrderId())));
        return result;
        
    }

private static List<Long> toOrderIds(List<OrderQueryDto> result) {
        List<Long> orderIds = result.stream()
                        .map(o->o.getOrderId())
            		   .collect(Collectors.toList());
        return orderIds;
    }


private Map<Long, List<OrderItemQueryDto>> findOrderItemMap(List<Long> orderIds) {
        List<OrderItemQueryDto> orderItems = em.createQuery(
            "select new jpa.practice2.jpa2.repository.order.query" +
			".OrderItemQueryDto(oi.order.id, i.name, oi.orderPrice, oi.count)" +
                                " from OrderItem oi" +
                                " join oi.item i" +
                                " where oi.order.id in :orderIds", 	
							OrderItemQueryDto.class)
                .setParameter("orderIds", orderIds)
                .getResultList();

        //map으로 바꾸는 과정
        Map<Long, List<OrderItemQueryDto>> orderItemMap = 
				orderItems.stream()
                .collect(Collectors.groupingBy(orderItemQueryDto -> 
											orderItemQueryDto.getOrderId()));
// System.out.println("orderItemMap : " + orderItemMap);
// 위에 map을 print하게 되면 이런식으로 나온다
// 즉 grouping by는 id와 OrderItemQueryDto을 서로 묶어주는 역할을 하는 것
// 화살표 뒤가 key값 같은 역할을 하는 것처럼 보인다.
/*orderItemMap : {
4=[OrderItemQueryDto(orderId=4, itemName=JPA1 Book, orderPrice=10000, count=1),
  OrderItemQueryDto(orderId=4, itemName=JPA2 Book, orderPrice=20000, count=2)],
    
11=[OrderItemQueryDto(orderId=11,itemName=spring1 Book, orderPrice=20000,count=3),
OrderItemQueryDto(orderId=11, itemName=spring2 Book, orderPrice=40000, count=4)]}*/


        return orderItemMap;
    }
```

- 이렇게 사용할 시  Query : 루트 1번, 컬렉션 1번 호출하게 된다. 
- ToOne 관계들을 먼저 조회하고, 여기서 얻은 식별자 orderId로 ToMany 관계인 OrderItem 을 한꺼번에 조회
- MAP을 사용해서 매칭 성능 향상(O(1)

