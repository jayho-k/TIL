# 뉴비 가이드 라인 정리 by [pr0gr4m](https://github.com/pr0gr4m)

 취업 참고

- https://doodreamcode.tistory.com/30 백엔드 공부트리
- https://i.am.ai/roadmap/#note 데이터 관련분야 로드맵

- https://github.com/teddylee777/machine-learning?fbclid=IwAR0MEdKpDydm6fyoRaidZ7Qd4HHXnxE3lZ_PKIaqm9GYCfWRCiks4mQx6es 인공지능 스스로 공부하기 (정리)



## 선수지식

- 영어
  - 새로운 지식과 관련된 정보일수록 영어로 되어있기 때문



## 언어

- 언어를 배우는데 시간을 과투자해서 배울 필요가 없다 
  = 하나를 마스터하고 필요할 때 마다 언어를 익히자

- 주무기 2개 + 보조무기 1개

  - 주무기: 
    원하는 로직을 자유롭게 구현할 수 있을 정도/
    장단점을 알고 그 언어의 특색에 맞게 사용할 수 있을 정도
  - 보조무기: 
    쓸만한 프로그램 구현

  

## 언어

- 파이썬:
  - 러닝 파이썬
  - 전문가를 위한 파이썬



## 핵심 공부 테크닉

- 알고리즘
- 컴퓨터 구조
- 운영체제

이러한 내용들의 공부가 필요하다

### 알고리즘

아카데믹, 실무, 취업 등에 따라서 또한 분야에 따라서 사용하는 알고리즘들이 달라지게 된다. 어느 분야에 관심이 있는지 알아보고 어느 알고리즘이 즐거운지 파악을 한 후 이에 관련된 알고리즘과 분야에 대해서 공부하고 취업을 하는 것이 좋아보인다.

#### Academic

- [Foundations of Algorithms](http://www.yes24.com/Product/Goods/11999564)
- [Project Euler](https://projecteuler.net/) : 유명한 PS 플랫폼으로 여타 다른 플랫폼과는 다르게 수학 문제를 해결하는 사이트입니다. [한국어 번역 사이트](https://euler.synap.co.kr/)도 있지만 몇 기능과 문제들이 넘어오지 않았습니다. 수학 문제들을 프로그래밍을 통해 해결해보고 싶은 분들에게 추천합니다.

#### coding test

- 파이썬 알고리즘 인터뷰
- 이것이 취업을 위한 고딩테스트다

- [LeetCode](https://leetcode.com/): 유명한 해외 PS 플랫폼입니다. 양질의 문제가 매우 많으며 구글, 아마존, 페이스북, 넷플릭스 등 해외 기업들의 기출 문제들도 풀 수 있습니다. 위의 파이썬 알고리즘 인터뷰 서적 또한 해당 플랫폼에 있는 문제들을 풀이하며 설명합니다. 흔히 코딩 테스트 양치기를 하기에 가장 좋은 플랫폼 중 하나입니다.



### Computer Architecture

- [Computer Organization and Design](http://www.yes24.com/Product/Goods/12716580) : 컴퓨터 구조의 바이블
- [프로그래머가 몰랐던 멀티코어 CPU 이야기](http://www.yes24.com/Product/Goods/3858484) 
  - 컴퓨터 구조를 공부한 적이 없는 사람이 읽어봤으면 하는 서적
- [프로세서를 지탱하는 기술](http://www.yes24.com/Product/Goods/5903582)
  - 위의 멀티코어 CPU 이야기와 약간 비슷한 성격의 서적인데 좀 더 프로세서의 근간이 되는 내용을 설명해줍니다. 마찬가지로 굉장히 좋은 서적이지만 아쉽게도 절판입니다. 혹시 도서관에서 빌려볼 수 있다면 한번 읽어보기를 추천합니다.



### 시스템 프로그래밍

어플리케이션(응용프로그램)으로 하여금 computing하는 환경을 제공해주는 소프트 웨어이며, 하드웨어와 밀접하게 관련되어 있다.

#### 종류

- 컴파일 시스템
- 운영체제 시스템
- 런타임 시스템

#### 컴파일 시스템

- editor >compiler > assembler > linker > loader 를 통해 고급언어를 어셈블리 언어로 바꾸어 준다 ==> 기계어(machine language)로 바꾸어 준다. ==> 실행가능한 파일로 만들어주는 시스템



####  운영체제 시스템

- 컴퓨터가 돌아가는데 필요한 전체적인 동작을 제어해주는 시스템



#### 런타임 시스템

- 라이브러리 함수, 쉘 뿐만 아니라, database나 mutimedia와 같이 기본적인 운영체제에서 지원이 되지 않지만 어플리케이션이 도는데 필요한 추가적인 기능을 제공해주는 시스템

### Design Pattern

- [Head First Design Patterns](http://www.yes24.com/Product/Goods/1778966) : 유명한 디자인 패턴 입문서입니다. 사실 개인적으로 Head First 시리즈를 선호하는 편은 아니지만, 디자인 패턴만큼은 패턴들을 이해하고 익히기 좋은 예제로 잘 구성되어 있어서 예외로 두고 있습니다. 아래 GoF 서적이 디자인 패턴의 바이블이긴 하지만, 내용이 딱딱하고 일부 이해하기 쉽지 않아서 디자인 패턴을 처음 공부할 시에는 해당 서적으로 공부하는 것을 추천합니다. 참고로 디자인 패턴을 적용할 일이 많은 java로 작성되어 있습니다.
- [GoF의 디자인 패턴](http://www.yes24.com/Product/Goods/17525598) : 디자인 패턴의 바이블입니다. 참고로 GoF는 Gang of Four이라고 불리는 Gamma, Helm, Johnson, Vlissides를 줄인 것입니다. 디자인 패턴을 처음 공부하시는 분들보다는, 디자인 패턴을 한 번 정도 공부한 적이 있고 이제 실제 코드에 적용하려고 할 때 레퍼런스가 필요한 경우 해당 서적을 참고하는 것을 추천해 드립니다. 참고로 C++ 언어를 기반으로 작성되어 있습니다.

### OS

- [Operating System Concepts](http://www.yes24.com/Product/Goods/78225791) : 소위 공룡책으로 유명한 OS 개념 바이블 서적으로 많은 대학들에서 수업 교재로 사용하고 있습니다. 안타깝게도 최신 운영체제들의 기술들을 반영하고 있지는 못하지만, 근본적인 개념을 익히기엔 여전히 가장 좋은 책 중 하나입니다. (사실 본격적인 운영체제 공부를 처음 하는 독자들을 대상으로 최신 기술들을 가르치는 것도 너무 복잡하기에 무리가 있습니다.) 굉장히 역사가 깊은 책이라 여러 판이나 버전이 있는데, [에센셜](http://www.yes24.com/Product/Goods/71048173) 버전은 역서도 나와있습니다. 해당 서적은 최신 운영체제 기술을 공부하는 목적이 아닌 운영체제 개념을 처음 공부하는 분들에게 추천하며, 8판 이후 아무 버전 혹은 에센셜 버전으로 봐도 무방합니다.
- [64비트 멀티코어 OS 원리와 구조](http://www.yes24.com/Product/Goods/65061299) : OS를 부트로더부터 GUI까지 전부 만들어보는 서적입니다. OS를 만들어보는 컨텐츠를 여럿 봤지만 해당 서적이 가장 범용적이고 내용 구성이 좋았습니다. OS를 전문적으로 공부해보고 싶은 분에게 굉장히 추천드리는 책입니다. 참고로 내용이 정말 어렵습니다. 간신히 따라가다가도 APIC 같은 챕터에서 막힐 수밖에 없습니다. 그래도 포기하지 않고 내용을 다 이해하신다면 시스템에 대한 이해도가 크게 향상될 것입니다.

### Network

- [TCP/IP가 보이는 그림책](http://www.yes24.com/Product/Goods/73020774) : 네트워크라는 분야를 아예 처음 공부하는 사람이 보기에 좋은 책입니다. 그림책이라는 이름 답게 정말 기초적인 내용을 쉽게 설명해주고 있습니다. 깊이 있는 학습을 할 수는 없지만, 네트워크에에서 사용하는 기본적인 개념 지식들을 탑재하여 이 후 공부를 수월하게 할 수 있습니다.
- [후니의 쉽게 쓴 시스코 네트워킹](http://www.yes24.com/Product/Goods/89520426) : 한국에서 정말 전통적으로 쓰인 네트워크 기본 서적입니다. 저 또한 해당 서적으로 네트워크 분야에 입문했는데 당시에 초록 책으로 유명하던 서적이 파란 색으로 리뉴얼 되어서 조금 놀랐습니다. 사실 개발자분들보다는 네트워크 엔지니어분들에게 필요한 내용들을 학습할 수 있는 서적이긴 하지만, 범용적인 네트워크 기본 지식을 공부하고 싶은 분들에게 추천합니다.
- [IT 엔지니어를 위한 네트워크 입문](http://www.yes24.com/Product/Goods/93997435) : 개발 공부를 하다가 네트워크에 대한 전문적인 지식이 필요해졌을 때 보기 좋은 서적입니다. 혹은 위의 후니 책을 보고 복습 겸 좀 더 전문적인 내용까지 다루고 싶다면 해당 서적을 읽으면 좋습니다. 사실 이 글을 보는 대부분의 분들은 네트워크 엔지니어보다는 개발자를 목표로 할 것으로 예상되는데, 이러한 경우엔 위 후니 책보다 해당 서적을 좀 더 추천드립니다.
- [TCP/IP Illustrated](http://www.yes24.com/Product/Goods/4739649) : 고 Stevens가 쓰신 TCP/IP 네트워크의 바이블입니다. 총 3권으로 구성되어 있는데, 특히 1권은 네트워크 관련 개발을 하려는 모든 분들이 꼭 봐야할 필수 서적입니다. 참고로 번역된 적이 있긴 한데, 번역의 퀄리티가 정말 좋지 않아서 꼭 원서로 봐야합니다.

### Web

### Database

- [Real MySQL](http://www.yes24.com/Product/Goods/6960931) : 데이터베이스를 학습함에 있어서 DBMS와 SQL 학습은 필수불가결합니다. 해당 서적은 세계에서 가장 많이 쓰이는 RDBMS인 MySQL을 국내에서 가장 상세하게 설명한 책입니다. 다만 굉장히 상세하고 실전적이라 처음 데이터베이스를 공부하는 분에게는 조금 버거울 수 있습니다. 그런 분들은 [모두의 SQL](http://www.yes24.com/Product/Goods/64434562)같은 입문서를 한번 빠르게 보거나 인터넷에 있는 쿼리문 예제들을 실습해보며 쿼리문을 조금 익히고 해당 서적을 보는 것을 추천합니다.
- [파워 오브 데이터베이스](http://www.yes24.com/Product/Goods/69775589) : 세계적으로 유명한 데이터 베이스 설계 지침서인 '가장 쉬운 데이터베이스 설계'의 개정판 입니다. 이 서적은 특정한 DBMS나 SQL에 종속된 내용이 아닌 데이터베이스를 어떻게 설계하고 이용해야 하는 지에 대한 가이드를 잡아줍니다. 즉, 데이터베이스를 공부해본 적이 있어서 DBMS를 사용할 줄 아는 분이 데이터베이스를 어떻게 설계해야하는 지에 대하여 학습할 때 굉장히 추천드립니다.





























