# 04_CPU_Scheduling

![image-20220316105317724](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220316105317724.png)

- ##### I/O bound job

  - 빨강색 ==> cpu를 짧게 쓰는 프로그램
  - 즉 i/o를 자주 연산 해주는 것
  - 주로 사람과 interaction을 많이 함
  - cpu burst(cpu가 한번에 계산하는 기간 )가 짧아짐

- ##### cpu bound job

  - 파랑색 ==> cpu를 길게 쓰는 프로그램
  - 복잡한 계산을 요구할 때
  - cpu burst(cpu가 한번에 계산하는 기간 )가 길어짐



#### CPU Schduler

- 누구한테 CPU를 줄지 결정을 하는 것



#### Dispatcher

- CPU의 제어권을 다른 프로세스에게 넘긴다
- 즉 context switch라고 한다.



#### 상태변화가 있는 경우

- ##### 1,4 ==> nonpreemptive(= 강제로 빼앗지 않고 자진 반납)

- ##### 2,3 ==> preemptive(=강제로 빼앗음)

1. running => blocked : I/o systme call

2. running => ready : 할당 시간 만료

3. blocked => ready : I/O 완료후 인터럽트

4. terminate



## 1. 성능 척도(Perfomance Measuer)

주방장과 비유하심

- ##### CPU utilization(이용률)

  - CPU는 바쁠 수록 좋은 것
  - 얼마나 바쁜지

- ##### Throughput(처리량)

  - 시스템입장에서 보는 것
  - cpu가 얼마나 일을 했으냐
  - 처리량이 많을 수록 좋음
  - 손님을 얼마나 받았는지

- 손님 입장

- ##### Turnaround time

  - 특정 프로세스가 일한 시간
  - 큐에서 기다리는 시간과 cpu를 사용한 시간의 합 (+ 밥먹은 시간)
  - 시간이 짧을수록 빨리 끝냈다는 것

- ##### Waiting time

  - 처음으로 들어온 시간이 아니고 들어온 시간의 합
  - 즉 권한을 빼앗기고 뒤로 물러났을 수도 있기 때문에
  - 대기 시간이 짧을수록 좋음
  - 예를 들어 웨이팅시간, 음식 기다리는 시간, 웨이터가 오는 시간 등등등등

- ##### Response time

  - cpu를 쓰려고 들어와서 부터(ready) 어떤 프로세스가 최초로 cpu를 얻기까지 시간
  - 식당에 가서 웨이터가 빨리 오는지 안오는지



## 2. Scheduling Algorithms

#### FCFC(First come First served)

- 먼저 온 것이 먼저 처리한다.
- nonpreemptive(빼앗지 않음)
- convoy effect
  - long process가 먼저 오면 short process가 너무 오래 기다리게 되는것
  - 그렇다면
  - 평균 waiting time이 매우 길어진다.



### SJF(shortest job first)

- 가장 짧은 것에 주는 것
- 평균 대기시간 짧음
- SJF is optimal (이것보다는 짧을 수 없음)
- 종류
  - nonpreemptive
  - preemptive
    - 짧아서 줬는데 더 짧은 애가 오면 걔를 준다
- 문제점:
  - 공평성에 문제(Starvation)
  - long process가  처리 안될 수 있음
  - 애초에 얼만큼 짧게 쓸지 알지를 못함

![image-20220316210648426](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220316210648426.png)

![image-20220316212737158](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220316212737158.png)

- 그럼 어떻게함?
  - 과거에 cpu burst가 얼만큼 썼는지를 보고 예측을 함
  - 예측 값 = a*실제 전에 사용한 시간 + (1-a)\*전에 예측 값
  - 예전에 것을 더 적게 반영하게 되고 직전 것은 더 많이 반영하게 된다. 



### Priority Scheduling

- 1 = 우선순위가 높음
- SJF는 일종의 Priority Scheduling이다
- 문제점
  - Starvation: 중요하지 않은 것 들

- 해결방법
  - Aging: 나이가 먹으면 즉 오래기다리면 prioty를 높여주자



### Round Robin

- q = 할당시간

- 각 프로세스는 동일한 크기의 할당 시간을 가지고 있음

- 시간 지나면 빼앗김

- 어떤 프로세스도 (n-1)q time unit 이상 기다리지 않는다.

- ##### 성능

  - q가 크면 => FCFS
  - q가 작으면 ==> cpu가 쓰려고 하면 뺏기고 쓰려고 하면 뺏기다
    - 그럼 오버헤드가 커진다(context switch때문에)

- 장점

  - SJF보다 average turnaround time은 더 길지만 respose time(단무지, 웨이터)은 더 짧다
  - 동일한 job들이 있는 것이아니라 여러 job이 합쳐져 있다.

- 단점

  - 모든 작업이 끝나서 나갈때 한번에 모여서 나가게 된다
  - 예를 들어 은행에 10분 정도 작업 10명을 10초씩 봐주는 느낌
  - 이게 좋은가??
  - 아님



### Multilevel Queue

![image-20220316221103727](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220316221103727.png)

- 여러줄로 줄서는 것 ==> CPU가 하나인데??

- 어떻게??

  - ##### foreground(intractive) 

    - (시간 짧은 애들) 
    - ==> RR(로빈)을 쓴다

  - ##### background(batch - no human interation)

    -  (시간 긴애들)
    - ==> FCFS(빨리 온애 처리)

  - ##### Fixed priority scheduling

    - foreground가 비워지면 그때 background을 처리
    - stavation의 가능성이 있다

  - ##### Time slice

    - 각 큐에 CPU Time을 적절한 비율로 할당
    - ex) 80%는 foreground inRR, 20% background inFCFS



### Multilevel Feedback Queue

- 여러줄 있음

- 줄간에 이동이 가능 ==> 신분상승, 신분하락 가능

- aging방식으로 구현이 가능함

- 특징

  - 각각의 큐의 scheduling algorithm

  - Process를 상위 큐로 보낼수 있음

  - Process를 하위 큐로 보낼수 있음

  -  CPU를 얻을때 들어갈 큐를 결정하는 기준



- Example

![image-20220316221430487](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220316221430487.png)

1. 8만큼 처리를 다 못함
2. 16으로 가등시킴 ==> 16초동안에 시간이 있음
3. 16초 안에도 못끝냄?
4. FCFS로 강등당함
5. 위에 다 해결 될때까지 밑에 있는 애들은 못나옴
6. 이것은 그냥 하나의 예시 중 하나다



특징있는 scheduling

### Multiple- Processor Scheduling

- ##### Homogeneous processor인 경우

  - 모두 같은 성능을 가진 경우
  - Queue에 한줄로 세워서 각 프로세서가 알아서 꺼내가게 할 수 있다
    - 즉 은행원 창구같은 느낌
  - 특정 프로세서에서 수행되게끔 할 수 있음
    - 예를 들어 미용실에서 특정 미용사한테 머리를 맡기는 경우
    - 문제가 더 복잡해지게 된다.

- ##### Loading sharing

  - job들이 특정 cpu에 가지 않도록 잘 분배되게끔 하는 메커니즘 필요
  - 별개의 큐를 두는 방법 vs 공동 큐를 사용하는 방법

- ##### Symmetric Mulitprocessing(SMP)

  - 각 CPU들이 알아서 스케줄링 결정

- ##### Asymmetric Mulitprocessing

  - 하나의 CPU가 대장
  - 데이터의 접근과 공유를 책임짐
  - 나머지 CPU는 거기에 따름



### Real-Time Scheduling

- Hard real-time sys
  - 데드라인을 지키는 것이 워낙 중요한
  - 오프라인으로 arrive타임을 미리 알고
  - 얼만큼 cpu를 쓸지 계산을 함
- soft real-time computing
  - 일반 프로세스에 비해 높은 priority갖도록 해야함
  - ex) 동영상



### Thread Scheduling

- 하나의 프로세스 안에 cpu수행 단위가 여러개 있는 것

- Local Scheduling
  - user level thread
    - 운영체제는 thread의 존재를 모름
    - 사용자 프로세스 본인이 내부에 여러개 thread를 넣는거
    - 내부적으로 누구에게 cpu를 줄지 결정
- Global Scheduling
  - kernel level
    - 운영체제가 thread의 존재를 앎
    - 운영체제가 어느 thread에게 cpu를 줄지 결정을 하는 것



## Algorithm Evaluation

- 그래서 어떤 알고리즘이 좋은건데?

  - ##### Queueing models

    - 확률 분포로 주어지는 arrival rate와 service rate 등을 통해 각종 performance index값을 계산
    - 이렇게 하면 처리량,과 대기 시간이 나오게 된다.
    - 옛날에는 이런 방법을 사용

  - ##### Implementation and Measurement

    - 실제 시스템에 알고리즘을 구현
    - 실제 작업에 성능을 측정
    - 비교(original linux vs 내가 바꾼 linux) 누가 더 좋음?
    - 굉장히 잘하는 사람이 할 수 있음

  - ##### Simulation

    - 모의 프로그램으로 작성
    - trace(실제 프로그램에서 뽑아서)를 입력 넣음
    - 비교



