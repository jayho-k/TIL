# G1

최대 힙 크기를 설정하고 나머지는 JVM과 GC에 맡기는 것

- Generational
- Incremental
- Parallel
- Mostly Concurrent
- Stop the World
- Evacuating



Incremental

- Region을 균일한 크기로 나눈다(JDK18부터 최대 512MB까지 가능)
- young region과 old region이 존재하는데 힙의 일부 영역만 항상 활정화된다.
  - 그래서 많은 항목이 회색으로 표시된다.
- 증분형 가비지 수집기는 젊은 영역만을 자주 스캔한다.
- 가끔 혼합 수집을 한다.
  - young region과 함께 일부 old region도 수집
- 가장 많은 가비지와 가장 도달할 수 없는 객체가 있는 영역을 선택해서 메모리를 회수한다.



Remembered Set, 

```java
Person { // 1번 region에 저장되어있음 => 100번 region에 Address를 참조하고 있음
    int age;
    Address address
}

Address{  // 100번 region에 저장되어있음
    ...
}
```

- Person은 Address를 참조하고 있음

  - 위와 같이 참조하고 있는 형태를 지역 간 참조라고 한다.

- 오래된 지역 간 참조가 지역 경계를 넘는 경우 가 종종 있다.

- 이럴 떄 GC는 기록함

  - 왜냐하면 하나의 지역만 수집 대상이 될 수 있기 때문임
  - Address가 포함된 지역은 회수, Persion이 포함된 지역은 회수되지 않을 수 있음

- G1은 R Set을 사용해서 지역 간 참조가 업데이트 되었는지 확인 할 수 있음

  - 따라서 Application은 Person 인스턴스로 작업할 때 Address의 현재 위치를 검색할 수 있음

    

- 지역 간 참조가 중요하게 여겨지는 경우

  - old region에서 young region으로 지역간 참조는 중요하게 여긴다.
  - 왜냐하면 오래된 지역은 가비지 수집에 포함되지 않을 수 있기 때문
  - 따라서 업데이트 해야 할 수도 있음

- 지역 간 참조가 중요하게 여겨지지 않는 경우.

  - 모든 젊은 지역이 모든 가비지 수집에 포함되기 때문이다. 
    - 즉 젊은 지역 간 지역간 참조는 중요한 대상이 아니게 된다.
    - 또한 young에서 old로의 지역간 참조도 중요한 대상이 아니게 된다. 왜냐하면 참조가 젊은 지역에서 시작되었기 때문이다.



Write Barrier

- 지역 간 참조를 어떻게 인식하는지에 대한 해답
- 쓰기 장벽은 Application 코드가 참조 값을 수정하는 곳에 삽입된다.

```java
public class Person{
    int age;
    Address address;
	public void setAddress(Address address){
        // <write barrier injected here>
        this.address = address;
        // <write barrier injected here>
    }
}
```

1. 참조가 같은 region에 위치하는지
2. 새 값이 null인지
3. 영역이 새로운지
4. 기억된 집합과 같은 모든 필수 업데이트 및 회계를 수행



C set : GC가 수집을 위해 지정한 영역

**G1이 젊은 영역에 새 객체를 할당하지 않을 떄 발생하는 예외**

- 거대한 객체 : 설정된 영역 크기의 절반보다 큰 객체
- 가장 가까운 영역 크기 증가에 맞춰 별도의 영역에 배치
- region을 16MB로 설정
  - 9MB 객체는 별도의 16MB에 배치
  - 17MB는 2개의 연속된 16MB영역에 배치
  - **Huge 객체는 Young Generation에 배치되지 않는다.** 하지만 기술적으로는 Old Generation에도 배치되지 않는데, 이건 모든 가비지 수집 시 검사되기 때문



Parallel

동시성 가능

- 장점
  - stw 시간이 줄어들게 된다.
  - 즉 Application이 실행되는 동안 수행할 수 있음
  - 더 많은 힙을 처리할 수 있음
- 단점
  - 동시에 수행한다는 것 : Application이 사용할 수 있는 CPU 리소스를 차지한다는 것
  - GC의 아키텍처가 복잡해져 시스템 무결성을 유지하는데 필요한 추가적인 기록 및 검사로 인해 메모리와 CPU 오버헤드가 증가



G1 사이클 

- G1은 특정 활동에만 동시에 수행하며 동시 단계가 항상 실행되지 않음
- G1은 2단계로 나뉨
  - Young Only : Young Region만 회수한다.
  - Space Reclamation : 혼합 수집(오래된 영역과 젊은 영역으 모두 회수)

1. Young Only 단계
   - Old 세대의 사용량이 특정 임계 값인 Initiating Heap Occupancy Threshold에 도달하면, Young-only 단계에서 **공간 회수(Space Reclamation)** 단계로 전환된다.
     - **공간 회수(Space Reclamation) 시점에 Concurrent Start Young Collection을 스케줄 한다.**
   - YoungGC가 수행된다.
     - Young Generation 리전들을 대상으로 접근가능한 객체를 찾아낸 후 일정 임계치를 넘지 않은 객체들은 서바이버 리전으로 복제(Copy)한다.
     - 임계치를 넘은 리전들은 Old Generation으로 승격된다.
     - 기존의 Young Generation은 가비지로 간주하여 메모리를 회수한다.
   - YoungGC가 수행되면 바로 Old GC가 발생
2. Concurrent Start Marking Process
   - 목적 : 공간 회수 단계 동안 오래된 영역을 회수하기 위한 힙을 준비하는 것
   - Old 세대 영역에서 현재 도달 가능한(live) 객체들을 찾아 다음 공간 회수 단계에서 유지할 대상을 결정합니다.
   - 마킹이 완전히 완료되기 전까지는 일반적인 Young Collection이 발생할 수 있음
   - 마킹은 Remark, Clean Up으로 마무리 된다. **이때 STW 가 발생한다.**
   - 해당 프로세스가 일시정지 중에 마킹을 계속할 필요가 없다고 판단된다면?
     - Concurrent Mark Undo Phase가 발생하고 Young-only 단계가 계속된다.
     - 이때는 Remark와 CleanUp이 발생하지 않음
   - **Marking**
     - 이전 단계에서 변경된 정보를 토대로 Initial Mark를 수행한다
     - GC 루트와 직접 연결된 객체들로 부터 시작해 객체 그래프 전체를 탐색
   - **Remark**
     - STW
     - 마킹 최종 확정
     - 참조 처리 ??
     - 클래스 언로딩, 완전히 비어 있는 영역을 회수하고 내부데이터 구조를 정리
     - Remark 와 Cleanup 사이에서, G1은 선택된 Old 세대 영역의 빈 공간을 나중에 동시적으로 회수할 수 있도록 정보를 계산
   - **Cleanup**
     - 실제로 공간을 회수하는 단계
     - 공간 회수단계를 진행할지 여부를 결정
     - 공간 회수단계가 진행될 경우 Young-only 단계는 하나의 **Prepare Mixed Young Collection**으로 마무리
3. Space Reclamation 단계
   - 이 단계는 여러 번의 Young 컬렉션으로 구성되며, Young 세대 영역뿐만 아니라 **선택된 Old 세대 영역의 live 객체들도 회수**합니다.
   - G1은 Old 세대 영역을 더 이상 회수하는 것이 충분한 빈 공간을 만들어내지 못한다고 판단되면, 이 단계는 종료됩니다.





1. Concurrent Mark

   1. Marking
      - 이전 단계에서 변경된 정보를 토대로 Initial Mark를 수행한다
      - GC 루트와 직접 연결된 객체들로 부터 시작해 객체 그래프 전체를 탐색
   2. Remarking
      - 전체 쓰레드가 함께 참가하여, 
      - STW가 발생하고
      - 표시 프로세스를 마무리하고, 클래스 언로딩을 수행하고 완전히 비어 있는 영역을 회수한다.
      - 동시적으로 Rset을 재구성한다. (시작 단계 스냅숏)
      - 재구성 이후  변경된 소수의 객체만 처리한다. 

   

Old Region Reclaim

- Old 리전에 대한 회수 단계
  - 여기도 Remarking, Evacauation Pause 단계가 포함
  - Remarking
    - 가비지 수집을 위해 살아있는 객체의 비율이 낮은 리전 중 몇 개를 추려내는 작업
  - Evacuation Pause : 
    - Young 리전에 대한 가비지 수집도 포함하며, 리마킹 단계에서 식별한 Old Region과 같이 수집이 된다.
    - 이렇게 함으로써, 생존률이 높은 리전들만 골라낼 수 있게되고 이 단계에서 Young / Old에 대한 작업이 동시적으로 수행되서 Mixed-GC라고도 부른다.





1. 공간 회수 단계 

   - 정기적으로 가비지 수집을 수행, 

   - 젊은 영역을 회수,

   - 자격이 있는 객체를 Old Generation으로 승격 시킴

   - 내부 추론에 따라 특정 시점에서 이전 지역이 차지하는 공간의 Threadhold를 초과하면 동시 현재 주기가 시작된다.

2. 동시 마크 사이클

   - 목적 : 공간 회수 단계 동안 오래된 영역을 회수하기 위한 힙을 준비하는 것
   - 동시 마크 프로세스
     - 젊은 세대만 일시 정지로 시작하여 이전 세대 점유 임계 값에 따라 동시 마크 단계에서는 객체가 현재 활성 상태인 이전 영역을 스캔한다. (어떤 이전 영역을 수집할지 결정하는 핵심 요소)
   - 재표시
     - 일시 중지가 발생
     - 표시 프로세스를 마무리하고, 클래스 언로딩을 수행하고 완전히 비어 있는 영역을 회수한다.
     - 동시적으로 Rset을 재구성하고 영역 스크럽 단계가 이어진다.
   - 복사 
     - Rset을 재구성
     - 선택된 이전 세대 영역에서 여유 공간을 회수한다.
   - 청소
     - 일정 시간 동안 동시 재구축 기억세트와 스크럽 영역 단계의 결과가 확정되고 공간 회수 단계가 이어질지 여부가 결정

3. 혼합 일시 중지 준비

   - 공간 회수 단계 동안 혼합 일시 중지 중에 수집해하는 최소 지역 수를 계산한다.

   - G1은 공간 회수 단계에 들어가고 이 단계 동안의 일시정지는 젊은 지역과 함께 동시 단계 동안 수행된 작업을 기반으로 오래된 지역도 수집된다.







STW

- GC의 아키텍처와 동작을 단순화하는데 확실한 이점이 있다.
- 애플리케이션이 실제로 사용 중인 참조를 실수로 이동하는 것에 대한 걱정이 없을 것이기 때문

Evacuating

- 도달 가능한 객체를 찾아 보존
- 아직 도달 가능한 객체를 새 영역으로 대피시키는 프로세스를 통해 발생하지만 실제로 객체는 이동하지 않고 새영역에 복사된다.

- Eden과 생존자라는 두가지 유형의 젊은 지역이 있음
- 새로 할당된 객체는 가비지 수집기에 Eden지역에 배치
- 에덴 지역에서 살아남은 객체는 생존자 지역으로 대피
- 생존자 지역에서 승격 가능한 객체는 새로 생성된 Old지역으로 승격된다.
- 생존자 지역 외에 지역은 회수된다.



거대한 지역

- 























