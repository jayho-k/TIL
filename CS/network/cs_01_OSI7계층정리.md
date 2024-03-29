# 01_OSI전체 정리

> - 1계층 : Physical
> - 2계층 : Data-Link
> - 3계층 : Network
> - 4계층 : Transport
> - 5계층 : Session
> - 6계층 : Presentation
> - 7계층 : Application

## 1계층 : Physical

- **역할**
  - bit신호를 **물리적인 전송 매개체**로 전달
  - **데이터를 전기적인 신호로 변환**해서 주고받는 기능을 진행하는 공간
  - 배선, 커넥터 등과 같은 물리적 연결 구조
  
- **PDU**
  - bit

## 2계층 : Data-Link
<3장 데이터 통신 참고>

- **역할**
  - 물리직인 연결
  - Flow Control (흐름 제어)
    - 하나의 네트워크 대역안에서 어떤 장비가 어떤장비에게 데이터를 전달할지 제어
  - Error Control (에러 제어)
    - 내가 보내는 데이터가 오류가 있는지 제어한다.

- **PDU**
  - Frame
    - Framing : 1111이나 0000같은 것으로 원본 데이터를 감싸는 작업

- **프로토콜**
  - Ethernet
    - 목적지 주소 (6Byte)
    - 출발지 주소 (6Byte)
    - 이더넷 타입 : 상위 프로토콜 내용이 존재(3계층 프로토콜을 미리 알려준다.)

- **주소체계**
  - MAC 주소
    - LAN에서 통신할 때 사용
    - 16진수로 사용



## 3계층 : Network
- **역할**
  - 라우팅, 목적지까지 데이터 전송
  - 다른 네트워크 대역(먼 거리)에 어떻게 데이터를 전달할지 제어
    - 즉 LAN과 LAN을 연결시켜주기 위함
  
- **PDU**
  - pocket

- **프로토콜**
  - ARP프로토콜
    - IP주소를 이용해 MAC주소를 알아오는 것
  - IPv4프로토콜
    - EAN에서 통신할 때 사용
  - ICMP프로토콜
    - 서로 통신되는지 확인할 때 사용


- **주소체계**
  - IP주소 : 
    - WAN에서 통신할 때 사용하는 주소

- **멀리 있는 것과 통신하기 위한 최소한의 설정**
  - IPv4
    - 현재 PC에 할당된 IP주소
  - 서브넷 마스크
    - IP주소에 대한 네트워크의 대역을 규정하는 것
  - 게이트웨이 주소
    - 외부와 통신할 때 사용하는 네트워크

- 서브넷 마스크란?
  - 어디까지가 네트워크 대역을 구분하는데 사용하고
    어디서부터 호스트를 구분하는데 사용하는지 지정
  - 규칙 : 1과 1사이에는 0이 올 수 없음 => 1연속 or 0연속

- 사설 IP와 공인 IP
  - 공인 IP
    - 인터넷 세상
    - 네트워크 통신망이랑 사용하는 IP주소
  - 사설 IP
    - 같은 네트워크 대역에서 사용하는 IP주소

- NAT
  - 특정 IP를 다른 IP로 바꾸는 기술
  - 이 기술을 이용해서 IP값을 공인 IP값으로 바꾸고난 뒤에 오부로 보낸다.

- ARP프로토콜는 어떻게 IP주소로 MAC주소를 알 수 있나?
  - 같은 네트워크 대역
  - ARP요청 : mac주소는 비워둔다.
  - 같은 네트워크 대역에 있는 모두에게 요청을 보낸다.
  - 본인 ip주소와 목적지 ip주소가 일치하는지 확인
  - 자신의 ARP응답
  
- Routing table
  - rounting table에 있는 네트워크 대상만 찾아갈 수 있고 없으면 찾아갈 수 없음
  - 그럼 만약에 routing table에 없는 네트워크라면?
    - 기본 설정값이 존재한다. => 이것으로 일단 문밖으로 나가게 된다.
    - 이후 네트워크 대역이 바뀔때 마다 ARP로 mac주소를 알아내서 보내게 된다.
    - 즉 일일히 수소문해서 알아가게된다는 뜻

## 4계층 : Transport

- 두 호스트 시스템으로부터 발생하는 데이터의 흐름을 제공
- TCP와 UDT프로토콜 사용
- port를 열어두고,, 프로그램들이 전송할 수 있도록 제공
- 데이터 단위 : Segment



## 5계층 : Session

- 통신 시스템 사용자 간의 연결을 유지 및 설정
- 데이터가 통신하기 위한 논리적 연결을 담당한다.
  - 세션을 만들어 내고 없애는 책임을 지고 있다.
  - TCP/IP 세션을 만들고 없애는 역할을 한다.
- API, Socket



## 6계층 : Presentation

- 세션 계층간의 주고받는 인터페이스를 일관성 있게 제공
- 파일 인코딩, 명령어를 포장,압축,암호화한다.
- JPEG, MPEG등



## 7계층 : Application

- 사용자가 네트워크에 접근할 수 있도록 서비스 제공
- HTTP등등





