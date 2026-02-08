# 02_Consumer



### Work Queues : Competing Consumers Pattern

- 메시지를 여러 Consumer 간에 분배하여 작업을 분산 처리하는 구조
- 작업 부하를 효율적으로 분산하고, 병렬 처리를 가능하게 만들어서 처리속도를 향상시키는 것

1. Round-Robbin, Fair Dispatch 방식을 사용해서 메시지를 Consumer 간에 분배하는 방식
2. Fair Dispatch 방식은 메시지 수동 확인(Manual Ack) 모드로 개발하고 메시지 처리 비중 설정등을 통새 조정 가능 >> 기본값 AUTO를 많이 사용한다.
   - Fair Dispatch 는 개발자가 설정을 개입해서 Consumer간에 조정을 하게 된다.
   - Fair Dispatch는 Ack모드를 수동으로 설정해야한다.



- Ready 상태 : 큐에는 들어갔지만 Consumer는 가져가지 않은 상태
  - **따라서 에러가 난 상태에서는 빠르게 코드를 수정이나, Purge를 시켜야한다.**
- Unacked 상태 : Consumer에게 메시지를 보냈지만 아직 처리를 안한 상태

-  Purge 하는 방법
  - Queues and Streams 창에 들어가서
  - Purge Messages를  눌으면 된다.
  - 이렇게 되면 message를 유실하는 것
    - 따라서 재처리가 가능하면 코드 수정 후 재수정을 해야하고 아니면 purge를 해주는 편이 낫다.





