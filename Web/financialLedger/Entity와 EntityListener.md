# Entity와 EntityListener



## @Entiry

- Entity : 이 클래스를 엔티티로 관리하겠다는 뜻을 가진 어노테이션

  - CreateEnottyManagerFactory를 로딩시점에 하나 생성하게 되고
  - createEntityManager를 통해 매니저를 만들어 엔티티를 통해 관리하게 된다.



## @EntityListeners

- Entity에서 이벤트가 발생할 때마다 특정 로직을 실행시킬 수 있는 어노테이션

- Persist, Remove, Update, Load에 대한 event 전과 후에 대한 콜백 메서드를 제공

- PreUpdate는 실질적으로 UpdateSQL문이 실행되었을 때 실행된다.
  - 즉 트랜잭션 종료 혹은 flush 하는 시점 따라서 PostUpdate와 동일하다고 볼 수 있음



## @AuditingEntityListener.class

- 사용하기 위해서 Application.java파일에 @EnableJpaAuditing을 추가해준다.

- @EntityListeners(AuditingEntityListener.class) 추가해준다.

- Auditing에서 데이터가 생성될 때 업데이트 해주길 바라는 변수에 @CreatedDate를 붙이고

- 업데이트 해주길 바라는 변수에 @LastModifiedDate를 붙인다.

-  @CreatedBy, @LastModifiedBy 도 존재



















