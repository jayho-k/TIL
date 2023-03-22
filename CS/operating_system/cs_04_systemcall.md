# cs_04_system call

**출처 :**

- https://didu-story.tistory.com/311
- https://mamu2830.blogspot.com/2021/01/whatIsSystemCall.html
- https://www.youtube.com/watch?v=v30ilCpITnY
- https://fjvbn2003.tistory.com/306

## 1. system call이란?

- 프로그램이 OS 커널이 제공하는 서비스를 이용하고 싶을 때 시스템 콜을 통해 실행
- **규칙**
  - 컴퓨터 대부분의 활동 => OS를 통해 실행
  - 실행중인 프로세스 => **자신의 프로그램 외 특정 파일 데이터를 필요**함?
  - => 파일을 읽고, 메모리에 데이터를 올리는 것 => OS역할 => OS허락요청
    - 운영체제가 관리하는 모든 자원(**네트워크, 디스크, 메모리 등**)을 **프로세스가 필요**로 할 경우 **시스템 콜을 사용**해야 한다.

- 시스템 콜 => **운영체제에서 만들어 놓은 코드**



## CPU모드

> - user mode
> - kernel mode

- User application이 시스템을 손상시키는 것을 방지하기 위해 존재
- 파일 읽기, 쓰기, 메세지 출력 등은 kernel mode에서 사용

<img src="https://blog.kakaocdn.net/dn/7d1fW/btrLwA292nm/3ldChPMmDQEO1fAQch2Vc0/img.png" alt="img" style="zoom: 50%;" />

### 1) User mode

- 사용자 App 코드가 실행
- 하드웨어에 접근 할 수 없음
- 접근을 위해선 System call 사용
- 각각의 스레드들은 stack영역을 가짐



### 2) Kernel mode

- OS가 CPU를 사용하는 모드
- 하드웨어를 제어하는 명령어를 실행



## System call의 종류



1. 프로세스 제어 (Process Control)

   - 끝내기(exit), 중지 (abort)

   - 적재(load), 실행(execute)

   - 프로세스 생성(create process) - fork

     

2. 파일 조작 (File Manipulation)

   - 파일 생성 / 삭제 (create, delete)

   - 열기 / 닫기 / 읽기 / 쓰기 (open, close, read, wirte)

   - 위치 변경 (reposition)

   - 파일 속성 획득 및 설정 (get file attribute, set file attribute)

     

3. 장치 관리 (Device Manipulation)

   - 하드웨어의 제어와 상태 정보를 얻음 (ioctl)

   - 장치를 요구(request device), 장치를 방출 (relese device)

   - 읽기 (read), 쓰기(write), 위치 변경

   - 장치 속성 획득 및 설정

   - 장치의 논리적 부착 및 분리

     

4. 정보 유지 (Information Maintenance)

   - getpid(), alarm(), sleep()

   - 시간과 날짜의 설정과 획득 (time)

   - 시스템 데이터의 설정과 획득 (date)

   - 프로세스 파일, 장치 속성의 획득 및 설정

     

5. 통신 (Communication)

   - pipe(), shm_open(), mmap()

   - 통신 연결의 생성, 제거

   - 메시지의 송신, 수신

   - 상태 정보 전달

   - 원격 장치의 부착 및 분리

     

6. 보호 (Protection)

   - chmod()
   - umask()
   - chown()













