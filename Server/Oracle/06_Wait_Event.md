# 06_Wait_Event

![image-20240330180327924](./06_Wait_Event.assets/image-20240330180327924.png)



### Idle Wait Event & Non Idle Wait Event

- Wait Event
  - **Idle Wait Event**
    - Timer, Message Sending, Client data waiting 등 리소스를 사용하지 않거나 클라이언트로 부터 답변을 기다려야하는 등의 Wait Event
    - DB 성능에 큰 영향을 미치지 않는 Wait Event 
      - 하지만 application 영향이 없는 것은 아니다.
  - **Non Idle Wait Event**
    - DB 내에서 Active Work 처리 과정 중에 발생하는 Wait Event
    - DB Time에 포함되어 중점적인 성능 모니터리인 요소인 wait event



### DB Time

- 정의	
  - DB Time은 User Process가 실제 일을 하면서 또는 DB에서 **waiting 되면서 사용된 총 시간**을 뜻한다.
    - Foreground 세션이 **DB call을 하여 자원을 사용한 총 시간**
    - CPU 시간, I/O 시간, Non Idle Wait Event시간 등으로 구성
      - ex_ parsing, excute, fetch 등
  - SQL을 처리하는데 있어서 어떤 자원을 사용했는지 등을 통하여 DB Time을 산출하게 된다.
  - **DB Time = CPU Time + Non Idle Wait Time** + Idle wait time
- 

- CPU Time보다 Non Idle Wait Time이 많으면?
  - CPU를 사용하는건 당연하다
  - 하지만 CPU가 다른 요소들 (Non Idle wait 등 )답을 가져오기는데 있어서 wait time이 크게 되면 비효율적으로 자원을 쓰고 있다고 할 수 있다.
  - 즉 Resource를 많이 사용하냐 안하냐는 wait time이 크냐 안크냐로 정의할 수 있음

<img src="./06_Wait_Event.assets/image-20240330182500850.png" alt="image-20240330182500850" style="zoom:80%;" />





### Wait Event Class

![image-20240330182603607](./06_Wait_Event.assets/image-20240330182603607.png)

- USER I/O
  - storage i/o를 Access할 때 나오는 I/O
- System I/O
  - back ground
- Concurrency
  - shared memory에 block을 Access할 때 Lock을 걸어주는 Latch같은 것
- Commit
  - load buffer가 Redo Log File에 write할때 발생하는 Wait/ redo와 관련되어있음



![image-20240330183155503](./06_Wait_Event.assets/image-20240330183155503.png)

![image-20240330183205928](./06_Wait_Event.assets/image-20240330183205928.png)



