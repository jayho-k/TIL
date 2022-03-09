# 02 structure of computer sys

## 운영체제 의미

- 좁은 의미(커널)
  - 운영체제의 핵심 부분으로 메모리에 상주하는 부분
- 넓은 의미
  - 커널 뿐 아니라 각종 주변 시스템 유틸리티를 포함한 개념
  - ex) 파일 복사



## 운영체제의 분류

- 동시 작업 가능 여부
- 사용자의 수
- 처리방식

#### 동시작업

- 단일 작업
  - 한 명령이 끝나지 전에 다른거 수행 x
  - 지금은 없음
- 다중 작업
  - 동시에 두개  이상의 작업 처리



#### 사용자의 수

- 단일 사용자
  - MS-DOS, MS Windows

- 다중 사용자
  - Linux, UNIX, NT server



#### 처리방식

- 일괄처리(batch processing)
  - 작업 요청의 일정량 모아서 한번에 처리 ==> 요즘은 사용 안함
- 시분항(time sharing)
  - 현대에 사용한다
  - 시간을 조금씩 분할해서 쓴다.
  - interactive한 방식을 사용한다.
- 실시간(Realtime OS)
  - dead라인이 존재한다.
  - 꼭 그 시간안으로 일이 종료되어야 한다.
  - ex) 원자로/공장 제어, 미사일제어, 반도체 장비 등등
  - 종류
    - hard realtime sys
    - soft realtime sys ==> 시간을 어겨도 크게 타격이 없을 경우 약간은 봐줌

- 범용 운영체제()

- 용어
  - Multiprogramming
    - 메모리에 여러 프로그램이 동시에 올라가 있는 것
  - Multi-processor
    - CPU가 여러개 붙어 있음을 의미
    - clouding computing 등에서 사용



#### 운영체제의 예

- 유닉스(UNIX)
  - c언어
  - 최소한의 커널 구조
  - 복잡한 시스템에 맞게 확장 용이
  - 소스 코드 공개
  - 프로그램 개발에 용이



- DOS(Disk Operating System)
  - 단일작업만 가능했었음



- MS Windows

  - 여러 프로그램을 동시에 돌리려고 함

  - 따라서 초반에는 불안정하다는 단점이 있었음

  - 하지만 지금은 안정하다 어느정도?

    

### 운영체제의 구조

![image-20220308203029752](02 structure of computer sys.assets/image-20220308203029752.png)











