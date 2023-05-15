# cs_06_Process_Synchronization



## 1_Race Condition

> - 조건
>
>   1. 여러 프로세스 => 동시에 데이터 접근
>
>   1. 접근 순서에 따라 결과값이 달라짐

### 1-1 ) 커널 모드로 수행 중 interrupt 발생

<img src="https://blog.kakaocdn.net/dn/Ocqh6/btrfG14dG6S/Ui7Kd1NRYDM0t02UKKVffk/img.png" alt="img" style="zoom: 67%;" />

- 커널 모드 중에 값이 바뀜
- 즉 count++과 count--가 모두 반영되어야 함
  - 그러나 그러지 못하는 경우
- 해결
  - 커널모드의 수행이 끝나기 전까지 인터럽트를 받지 않도록 한다.
  - **disable/enable**



### 1-2 ) 프로세스가 system call을 호출해서 커널모드로 수행중인데 Context switch가 발생

<img src="https://blog.kakaocdn.net/dn/b2HzMP/btrfw33k7qh/2sNwIKMlaknzor4TdpWrKK/img.png" alt="img" style="zoom: 50%;" />

- 두 프로세스는 데이터를 공유하지 않는다.
- 하지만 System call을 수행하는 동안에는 둘 다 커널 주소 공간의 데이터를 접근할 수 있음
  - 따라서 커널 주소 공간에서 작업을 수행하는 도중에 CPU를 빼앗긴다면? => race condition

- 해결방안
  - kernel mode를 수행 중일 때 CPU가 빼앗기지 않도록 한다. (preempt되지 않도록)
  - user mode로 돌아갈 때 preempt되도록 함



### 1-3 ) 멀티 프로세서에서  공유 메모리  내의  커널 데이터에 접근

<img src="https://blog.kakaocdn.net/dn/DoBj9/btrfJVoYJJ9/P63cPFZ42aI9bfpzcFsUfK/img.png" alt="img" style="zoom:50%;" />

- 논리적인 race condition이 나게 되는 경우
  - 즉 CPU가 여러개 => 동시에 같은 memory접근
- 해결
  - 공유 데이터에 접근 시 Lock/Unlock 방식을 사용해서 데이터 보호 



## 2_Critical Section

> - Race Condition이 발생할 수 있는 부분

**1. Mutual Exclusion (상호 배제)** 

- 이미 한 프로세스가 Critical Section에서 작업 중이면 다른 모든 프로세스는 Critical Section에 진입하면 안 된다.



**2. Progress (진행)**

- Critical Section에서 작업 중인 프로세스가 없다면, Critical Section에 진입하고자 하는 프로세스가 존재하는 경우 진입할 수 있어야 한다. 

 

**3. Bounded Waiting (한정 대기)**

- 프로세스가 Critical Section에 들어가기 위해 요청한 후부터 그 요청이 허용될 때까지 다른 프로세스들이 Critical Section에 들어가는 횟수에 한계가 있어야 한다. 
- 즉 **Critical Section에 진입하려는 프로세스가 무한정 기다려서는 안 된다.** 

 

## 3_ Synchronization Algorithms

### Algorithms_1

```c
do{
    while(turn!=0); // my turn?
    critical section;
    turn = 1;		// Now it is your turn
    remainder section;
} while(1);
```

- 과잉보호 => 반드시 한번씩 교대로 들어가야만 한다. 

- 현재 Critical Section에 들어갈 프로세스가 어떤 프로세스인지를 한 변수로 나타내어 일치하는 프로세스만 진입!

  - while ( 나를 가르키는 숫자)

  - turn = (상대를 가르치는 숫자)

  - critical section에 들어가기 전에 turn을 체크

    

- **문제점**

  - **Mutual Exclusion은 만족** => 동시에 들어가지는 않음
  - **Progress는 만족하지 못함**
    - 즉 상대방이 내차례를 주기 전까지는 critical section에 들어가지 못함



### Algorithms_2

 ```c++
 do{
     flag[i]=true; // Pretend I am in
     while (flag[j]); // is he also in? then wait
     // critocal section
     
     flag[i] = false;  // I am out now
 	// remainder section
 }while (1);
 ```

- critical section에 들어가고 싶다?
  - 그럼 깃발을 들게 된다. (flag[i]=true)
  - 이제 상대방에 깃발을 들고 있는지 확인을 하게 된다. (while(flag[j]))
    - 상대방에 flag가 있으면 기다린다
  - 상대방의 flag가 내려지면 critical section에 들어가게 된다.
  - 그리고 나올때 flag를 내리게 된다.

- **문제점**
  - Mutual Exclusion문제는 만족
  - Progress 문제
    - 깃발만 들고  cpu를 바로 빼앗기면?
    - 아무도 못들어가게 된다.



### Algorithm_3(Peterson's Algorithm)

-  알고리즘 1과 2를 합쳐놓은 개념

```c++
do{
    flag[i]=true;
    turn = j;
    while (flag[j] && turn == j); // 기다려
    critocal section
    flag[i] = false;
	remainder section
}while (1);
```

- 깃발을 이용
- 만약 둘이 동시에 깃발을 들었을 때
  - turn을 이용함
  - 즉 깃발을 든 친구들 한해서 turn을 하게 된다.

- **순서(i의 입장)**
  - 일단 깃발을 든다
  - turn을 상대방 turn으로 만들어 놓는다
  - 그 다음에 상대방이 깃발을 들고 있는지 + 이번 차례가 상대방 차례인지
    - 이때만 기다림
    - 즉 상대방이 깃발을 들고 있지 않거나 or  차례가 내 차례야?
    - 그럼 들어감
  - 들어감
  - 그리도 나올때 깃발 내림

**문제점**

- 작동은 제대로함 하지만 비효율적
- while문을 계속돌면서 기다리기 때문
  - busy waiting(spin lock) ==> CPU와 메모리를 쓰면서 계속 wait



## 4_Synchronization Hardware

- 알고리즘들이 복잡해진 이유

  - 데이터를 읽어가서 연산하고 저장하는 것이 한번에 일어나지 않음

  - 따라서 **중간에 뺴앗기기 때문에** 이런 문제가 생긴것이다.

- **하드웨어적으로 지원**이 있으면 이 문제는 쉽게 풀린다
  - 하드웨어적으로 test and modify를 *atomic*하게 실행을 하면 문제가 해결된다.
  - atomic : 중간에 데이터를 쪼개는 것 없이 반드시 한번에 실행



```c++
bool Test_and_Set(bool *target){
    bool rv = *target;
    *target = true;
    return rv
}
```

```c++
bool lock = false;
do{
    while (Test_and_Set(lock));
    critocal section
	lock = false;
	remainder section
}while (1);
```

- lock은 0 or 1
  - 0 => false => 아무도 락을 안 걸었다
  - 1 => True => 누군가 락을 걸고 그 안에 들어갔다

- 어느 방에 들어가서 문잠그고 모든 일처리를 하고 문을 열고 나온다.
  - => atomic

- 즉 하드웨어는 혼자 일을 해결하게끔 방을 하나 만들어준것이다.
  - 왜냐하면 **어차피 쪼개진 연산들을 한 덩어리로 처리**를 해줘야하기 때문이다



## 5_Mutex Locks

> Mutex  : Mutual Exclusion

**특징**

-  lock이 하나만 존재하느 locking 메커니즘
  - Critical Section에서 작업 중이면 다른 프로세스들은 Critical Section에 들어갈 수 없도록 한다.


-  Busy Waiting의 단점
  - **Spin Lock** => 만약 context switch비용이 더 든다면 spin lock이 더 이득
    - Critical Section에 프로세스가 존재할 때, 다른 프로세스들은 Critical Section에 계속해서 진입하려고 시도 => CPU를 낭비



## 6_Semaphores

> - 여러 프로세스나 스레드가 Critical Section에 진입할 수 있는 Signaling 메커니즘
> - 즉 방이 하나가 아니라 더 많다는 뜻
> - mutex는 세마포가 1로 가진다
> - 코드
>   - S : 방의 개수
>   - P연산 : 자원(방)을 획득 
>   - V연산 : 자원(방)을 반납

- **L**
  - block된 프로세스들이 기다리는 Queue이다.

- **block**

  - 커널은 block을 호출한 프로세스를 suspend시킴

  - 이 프로세스의 PCB를 semaphore에 대한 wait queue에 넣음

- **wakeip(P)**
  - block 된 프로세스 P를 wakeup시킴
    이 프로세스의 PCB를 ready queue로 옮김

```c++
typedef struct{
    int value;
    struct process *L;
} semaphore;
        
// P연산
void wait(semaphore S){
    S.value--;
    if (S.value<0){
        S.L (Queue)에 process를 넣는다;
        block();
    }    
}

// V연산
void signal(semaphore S){
    S.value++;
    if (S.value>=0){
        S.L에서 process P를 지운다.;
        wakeup(P);
    }
}
```

- 코드 설명
  - p연산
    - 세마포 값을 1뺀다
    - 세마포 값이 음수라면 block을 시켜라
  - v연산
    - 자원을 반납함
      - 자원을 반납했는데 0이하 = 누군가가 세모코를 기다리면서 잠들어있다
      - 양수 = 세마코가 남아돈다
    - 그래서 v가 0보다 크더나 같으면 하나 깨워줘서 ready상태로 바꿔준다



**더 좋은 알고리즘?**

- 일반적으로는 block and wakeup가 좋음

- 프로세스 상태를 바꾸는 것 = overhead

  

- Critica section의 길이가 긴 경우 (경쟁이 치열할 때)

  - block and wakeuprk가 좋음

  

- Critica section의 길이가 매우 짧은 경우 (경쟁이 치열하지 않을 때)

  - 오히려 busy wait를 하는 것이 좋을 수 있다

























