# cs_02_IPC

- 출처 : https://steady-coding.tistory.com/508

## IPC란?

- 프로세스들 사이에 **서로 데이터를 주고 받는 행위**
  - 프로세스들은 각각의 독립된 공간에서 실행되기 때문에 필요하다



## 01_IPC종류

> - Shared Memmory ( 공유 메모리 )
> - Message Passing ( 메시지 전달 )

### 1-1) Shared Memmory

<img src="https://blog.kakaocdn.net/dn/EFX2u/btrlxgu7n7I/xhHC7LUE6T1c75wg3dmeZk/img.png" alt="[운영체제] IPC - IPC 모델: Shared Memory" style="zoom: 50%;" />

#### Shared Memmory의 특징

- 두개 이상의 프로세스들이 주소 공간의 일부를 공유

  - 공유한 메모리 영역에서 read/write를 통해 통신

  

- **과정**

  - 프로세스가 kernel에게 공유메모리 할당 요청
  - kernel은 프로세스에게 메모리를 할당
  - 어떤 프로세스든 해당 메모리에 접근 가능
  - 공유 메모리가 설정되면, 그 후의 **통신은 커널과 상관없이 진행이 가능**



#### Shared Memmory의 장단점

**장점**

- kernel의 관여가 없음 => 속도가 빠름

- 프로그램 레벨에서 통신 => 자유로운 통신이 가능

  

**단점**

- **데이터를 읽어야하는 시점을 알 수 없음**
  - ex) 프로세스 A가 shared memory에 데이터 전달 => 프로세스 B는 그것을 알 수 없음
- 따라서 **동기화 기술**이 필요
  - 동시에 같은 메모리 위치를 접근할 수 있기 때문
  - **Lock**을 걸어서 해결



### 1-2)  Message Passing

<img src="https://blog.kakaocdn.net/dn/cmsQiy/btrlyZe6gQG/HgYGzkjztkHIrS6iLMT1S0/img.jpg" alt="[운영체제] IPC - IPC 모델: 메시지 전달 (Message Passing)" style="zoom:67%;" />

#### Message Passing의 특징

- **kernel 메모리 영역에 메시지 전달을 위한 채널**을 만듦
  - 협력하는 프로세스들 사이에 메시지 형태로 정보를 Send/Receive하는 방법
- **kernel을 경유하여 메시지를 송수신** => 커널에서는 데이터를 버퍼링함
  - ex) A프로세스가 kernel로 메시지 보냄 => B에게 메시지를 보내줌



#### Message Passing의 장단점

**장점**

- 동기화 로직이 없어도 된다.

**단점**

- kernel을 통해서 데이터를 주고 받음 => shared Momory보다 느림



## 02_Message Passing의 종류

> - Pipe
> - Message Queue
> - Socket

### 2-1) Pipe

<img src="https://blog.kakaocdn.net/dn/bLU3jo/btrlw3pc1Tq/QGTFg7JPXpiP3YGZymlma1/img.webp" alt="[운영체제] IPC - IPC 모델: 메시지 전달 (Message Passing) - 메시지 전달 모델의 예시 1 : 파이프" style="zoom:67%;" />

- Pipe는 stream 방식으로 동작 
- 두 개의 프로세스를 파이프로 연결 
  - 하나의 데이터는 쓰기만
  - 다른 프로세스는 읽기만
  - 따라서 단순한 데이터 흐름에 적합함
- 1:1통신이면서 **한 쪽 방향으로만 데이터 이동**
- 주로 부모-자식 간의 단방향 통신으로 사용
- 용량 제한 존재



### 2-2) Message Queue

<img src="https://blog.kakaocdn.net/dn/xcdtS/btrlxfbTf1c/ruckJjWEYpLVpkBkdFI5pK/img.jpg" alt="[운영체제] IPC - IPC 모델: 메시지 전달 (Message Passing) - 메시지 전달 예시 2: 메시지 큐" style="zoom: 50%;" />

- 메시지 ( 또는 패킷 )단위로 동작
- 부모/자식 관계가 아니더라도, 어느 프로세스 간의 데이터 송수신이 가능
- 양방향 통신 가능
- Memssage Queue에 쓸 데이터의 번호를 붙힘 => 다수의 프로세스가 동시에 데이터를 다룰수 있음
- 데이터가 많이 쌓일수록 추가적인 메모리 자원 필요
- 큐에 데이터를 넣고 나오는 과정에서 오버헤드 발생할 수 있음



#### 2-3) Socket

<img src="https://blog.kakaocdn.net/dn/dNYgaF/btrlwI6ICcA/V2GivlST2Cg8aJOH3IZfGK/img.png" alt="[운영체제] IPC - IPC 모델: 메시지 전달 (Message Passing) - 메시지 전달 예시 3: 소켓" style="zoom: 67%;" />

- Clien - Server 구조로 데이터 통신, **원격에서 프로세스 간 데이터를 공유**할 때 사용
- Port 번호를 이용하여 상태 프로세스의 socket을 찾아간다.
- Port를 사용하기 때문에 Local뿐만 아니라 Remote로도 사용할 수 있다. 
  - 다른 IPC는 local만 가능
- 양방향 통신 가능
- Internet UDP와는 달리 경로를 지정할 수는 없다.













