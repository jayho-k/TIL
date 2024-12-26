# Multitenant



## 스키마 분리를 통한 Multitenat 구현

> - 구현 필요
> - 

- CurrentTenantIdentifierResolver
  - tenatId를 제공하는 인터페이스다. 그래서 Entity에 tenantId를 넣어야한다.
  - 이 구현은 DB 연결을 위한 현재 tenantId를 결정한다.
  - 정작 보면 컬럼에 값이 있던데..? 
- MultiTenantConnectionProvider 
  - 각각의 tenant는 다른 스키마나 데이터베이스를 가질 수 있다.
  - 역할
    - 현재 tenant에 맞는 DB 연결을 제공. 즉 각각의 DB나 schema를 사용할 수 있도록 tenatId에 맞는 DB 연결을 동적으로 반환한다.
    - 각 tanent의 데이터는 다른 스키마를 저장한다. MultiTenantConnectionProvider는 쿼리 시 해당 스키마를 자동으로 분리하여 실행한다.
    - 즉 tenant Id 대신 MultiTenantConnectionProvider 를 작성하여 tenant 를 구분한다고 보면 될 듯 하다.



- 문제
  - 이전에 저장되어있는 db schema 값으로 들어가게 된다.
  - 그래서 찾아야하는 부분 : 
    - db schema가 바뀌는 타이밍 + 바뀐 schema를 언제 사용하는지

- 순서 (1에 넣고 싶지만 2에 넣어진 상황)
  - 요청이 왔음
  - resolveCurrentTenantIdentifier : multitenant2 인 상황
    - 용도 파악
  - getConnection을 하네 => multitenant2 인상황 
    - => 근데 얘는 어떤 용도로 쓰이는거지?
  - 그리고 setting을 시작하네 **맨 처음에 setting을 해야하는데 그게 안돼서 지금 이 문제가 발생하는 것**
    - setting에서는 multitenant1라고 뜨긴함 즉 set은 됐음 multitenant1
    - 이 set한 애를 언제 쓰는지가 모르겠네
  - save가 들어감
  - getConnection을 다시 하는데 이때 아직 multitenant2 임
  - save 완료 된 시점도 multitenant2 임
  - 실제 insert들어감 **save가 완료되고 나서 insert가 들어가는 것이 아님**

- 순서 (제대로 들어간 상황)

  - 요청이 왔음

  - setting 시작 multitenant2 

  - setting 완료 multitenant2 

  - resolveCurrentTenantIdentifier multitenant2  

  - getConection 스키마도 multitenant2

  - save 관련으로 넘어가서 save 시작

  - update seq 하고 releaseConnection multitenant2

  - insert 까지 하고 multitenant2

  - save 완료

    

- 문제점

  - transaction이 시작하기 전에 중간에 set이 안되는게 문제였음
    - 중간에 set이 안된다기보단 이미 setting이 transaction1로 잡혀있었음

  - 그리고 open-view 때문에 끝까지 transaction을 잡고 있어서 처음 시작할때 setting을 해도 안먹힌거임
    - transaction이 끝났는데도 반납을 안한거임 그래서 문제가 생긴거

- 일단 해결

  - open-view를 false로 뒀음 => 이거 원리 파악해야함
  - setting하는 부분을 transaction 시작하기 전에 진행했음





확인

- JpaTransactionManager 에서 doGetTransaction 함수
  - TransactionSynchronizationManager에서 toGetResource함수로 multitenant1 값을 얻네 (근데 )
  - 여기서 setEntityManagerHolder를 위에서 얻은 resource로 진행한다.



Controller에서 set을 해주면 어떻게 될까?

즉 transaction이 시작하기 전에 setting이 되어야함





