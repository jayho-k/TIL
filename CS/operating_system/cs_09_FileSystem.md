# cs_09_FileSystem

- 출처
  - https://rebro.kr/181

## 1) File/ File System

### File

- 비휘발성의 보조기억장치에 저장
- 운영체제는 다양한 저장장치를 file이라는 동일한 **논리적 단위**로 볼 수 있게 해준다.
- 연산 => create, read, write, reposition, delete, open,close



### File attribute ( meta data )

- 파일을 관리하기 위한 정보들
  - 파일이름, 유형, 위치, 사이즈 등
  - 시간, 소유자, 접근권한 등



### File system

- 운영체제에서 파일을 **관리**하는 부분
- 파일을 어떻게 **저장**할지
- 파일을 어떻게 **보호**할지
- 계층적 디렉터리 구조



### Partition

- 운영체제가 보는 디스크 = Logical Disk
  - C드라이브 D드라이브 등등으로 나누는 것



## 2) Access Method

> - 순차 접근 (Sequential Access)
> - 직접 접근 (Random Access)
> - 색인 접근 (Index Access)

### 2-1 )  순차 접근 (sequential)

<img src="./cs_09_FileSystem.assets/image-20230412143728310.png" alt="image-20230412143728310" style="zoom: 67%;" />

- 카세트 테이프를 사용하는 방식과 동일
- 현재 위치에서 읽거나 쓰면 offset이 자동으로 증가



### 2-2 )  직접 접근 (random)

- 임의의 순서로 접근할 수 있음
- 읽거나 쓰기 순서에 제약이 없음



### 2-3 )  색인 접근 (index)

- 파일에서 레코드를 찾기 위해 index를 먼저 찾고 대응되는 포인터를 얻는다.
- 이를 통해 파일에 직접 접근하여 원하는 데이터를 얻을 수 있다.
- 크기가 큰 파일에서 유용하다.





## 3 ) Ditrectory

- **파일의 메타데이터 중 일부를 보관**하고 있는 특별한 파일
- 기능
  - 파일 찾기 (Search)
  - 파일 생성 (Create)
  - 파일 삭제 (Delete)
  - 디렉터리 나열 (List)
  - 파일 재명명 (Rename)
  - 파일 시스템 순회 (Traverse)

파일을 빠르게 탐색, 그룹화를 하기 위한 방법



### 3-1 ) 1단계 디렉터리 (sinlge level directory)

- 모든 파일들이 디렉터리 밑에 존재하는 형태

<img src="./cs_09_FileSystem.assets/image-20230412144646332.png" alt="image-20230412144646332" style="zoom:67%;" />



### 3-2 ) 2단계 디렉터리 (Two Level Directory )

- 각 사용자별로 별도의 디렉터리를 갖는 형태

<img src="./cs_09_FileSystem.assets/image-20230412144752193.png" alt="image-20230412144752193" style="zoom:67%;" />

- UFD : 자신만의 사용자 파일 디렉터리
- MFD : 사용자의 이름과 계정 번호로 index되어 있는 디렉터리, 각 엔트리는 사용자의 UFD를 가르킨다.

- 장점
  - 효율적인 탐색이 가능하다.
- 단점
  - 그룹화가 불가능
  - 다른 사용자의 파일에 접근해야하는 경우 단점이 된다.



### 3-3 ) 트리 구조 디렉터리(Tree-Structured Directory)

- 사용자들이 자신의 서브 디렉터리(Sub-Directory)를 만들어서 파일을 구성
- 하나의 루트 디렉터리를 가진다.
- 모든 파일은 고유한 경로(절대 경로/ 상대 경로)를 가진다.
- 일반 파일인지 디렉터리인지 구분하는 방법
  - bit를 사용 => 0이면 일반, 1이면 디렉토리
- 장점
  - 효율적인 탐색 가능
  - 그룹화가 가능

<img src="./cs_09_FileSystem.assets/image-20230412145345743.png" alt="image-20230412145345743" style="zoom:67%;" />



### 3-4 ) 비순환 그래프 디렉터리(Acyclic-Graph Directory)

- 서브 디렉터리들과 파일을 공유할 수 있도록 한다.
- 트리 구조의 디렉터리를 일반화한 형태
- 절대경로명/상대경로명을 이용하여 **링크** 라고 불리는 새로운 디렉터리 항목을 만들 수 있다.
- 단순한 트리 구조보다는 융통성이 있는 대신에 더 복잡하다.

<img src="./cs_09_FileSystem.assets/image-20230412145511432.png" alt="image-20230412145511432" style="zoom:67%;" />



### 3-5 ) 일반 그래프 디렉터리(General Graph Directory)

- 순환을 허용하는 그래프
- 무한 루프에 빠질 수 있다.
- 하위 디렉터리가 아닌 파일에 대한 링크만 허용
- garbage collection을 통해 전체 파일 시스템을 순회, 접근가능한 모든것을 표시한다.



## 4 ) Allocation of File Data in Disk

> - Contiguous Allocation
> - Linked Allocation
> - Indexed Allocation

### 4-1 ) Contiguous Allocation

- 파일을 연속되게 저장하는 방식
- 디렉터리에 파일이 시작하는 부분, 파일의 길이 저장

<img src="./cs_09_FileSystem.assets/image-20230412150449851.png" alt="image-20230412150449851" style="zoom:67%;" />

- 장점

  - 한 번의 탐색으로 많은 양을 전송할 수 있다.

  - Random access가능

    

- 단점

  - 외부 단편화 발생
  - 파일의 크기를 키우기 어렵다.
  - 파일의 크기를 키워놓으면 내부 단편화 발생



### 4-2 ) Linked Allocation

- 파일의 데이터를 그냥 빈 위치에 넣음
- start 값과 end으로 Linked List 처럼 만들어서 비어있는 위치에 다 넣는것

<img src="./cs_09_FileSystem.assets/image-20230412150841217.png" alt="image-20230412150841217" style="zoom:67%;" />

- 장점

  - 외부단편화가 발생하지 않는다

    

- 단점

  - **직접 접근( random access ) 불가능** ==> 시간이 많이 든다

    - 이유 : 순회해야하기 때문

      

  - **Reliability**

    - 한 sector가 고장나 pointer가 유실되면 많은 부분을 잃는다.

      

  - **효율성이 떨어짐**

    - sector당 512바이트 단위로 맞춰져 있음(내부외부)
    - 근데 포인터 저장으로 4 bytes를 써버리면 맞춰놓은게 무너져버림

해결

- 이러한 단점을 보완하기 위해 FAT(File-allocation table)이라는 파일 시스템을 사용
- 포인터를 별도의 위치에 보관하여 신뢰성 문제와 공간 효율성 문제를 해결



### 4-3 ) Indexed Allocation

- **블럭하나에다가 인덱스 정보를 모두 저장**해놓음

<img src="./cs_09_FileSystem.assets/image-20230412151242016.png" alt="image-20230412151242016" style="zoom: 50%;" />

- 장점

  - 직접 접근 가능

  - hole이 생기지 않음

    

- 단점

  - 아무리 작은 파일이더라도 블럭이 2개 필요
    - index를 위한 공간
    - 정보를 저장하는 공간
  - 파일이 너무 크면 인텍스를 다 저장하지 못한다.
    - 해결
      - 마지막 인텍스는 다른 파일의 인테스를 저장 = linked list처럼
      - multi-level index



## 실제 파일 시스템

### UNIX 파일시스템의 구조

<img src="./cs_09_FileSystem.assets/image-20230412152123165.png" alt="image-20230412152123165" style="zoom:67%;" />

### boot block

- 모든 파일 시스템이 boot block이 있음 (UNIX만 있는 것이 아님)

- 부팅에 필요한 정보

  

### super block

- 파일 시스템의 어디가 빈블록이고, 파일이 저장되고, 사용중인지, 어디까지 Inode list가 있는지 등등

- 총체적인 시스템

  

### Inode list

- 인덱스 노드

- 파일 하나당 Inode하나가 부여된다

- 그리고 그 Inode는 파일의 meta data를 가지고 있음

- 위치정보, 사이즈, 타임 등등// 파일이름 , Inode번호 를 안가지고 있음 하지만 디렉토리 : 파일이름 , Inode번호 를 가지고 있음

- Inode는 크기가 고정되어 있음

- Inode list의 위치 정보

  - 효휼적인 이유: 대부분은 작은 파일이기 때문에

    

- **direct block**

  - 파일 크기가 작음 => direct인덱스만으로 표현이 가능함

    

- **single indirect**

  - 큰 파일일 경우 => 한번 따라가면 인덱스가 있음 => 거기 에 포인터가 있고 => 따라가면 파일 데이터가 있음

    

- **double indirect**

  - 더 큰 파일일 경우 ==> 두번 따라가면 위치 나옴

    

#### Data block

- file의 실제 내용을 보관한다
- 그리고 메타 데이터 중 일부를 보관
  - file name
  - Inode 번호



### FAT File System

<img src="./cs_09_FileSystem.assets/image-20230412152156923.png" alt="image-20230412152156923" style="zoom:67%;" />

### boot block

- 부팅 정보를 가지고 있음

  

### FAT

- 메타 데이터 중 일부를 보관

  - 위치 정보

  - 그 블록의 다음 블록을 저장해놓음

    

### Data block

- 모든 메타데이터를 가지고 있음

  - 파일이름, 권한, 사이즈, + 첫번째 위기가 어디인지까지를 모두 가지고 있음

    

- Linked Allocation이 가지고 있었던 문제점

  - 직접 접근 불가능 ==> 시간이 많이 든다

  - 한 sector가 고장나 pointer가 유실되면 많은 부분을 잃는다

  - 효율성이 떨어짐

    

- 어떻게 해결??

  - 다음 블럭을 data block을 FAT이라는 테이블에 저장하게 된다.

  - 순서

    - 217번 블럭의 정보 받음

    - 다음은??

    - FAT으로 감

    - 217번 찾음 => 618번에 있다고 함

    - 618번으로 감 => 339번 => EOF값이 나옴 => 끝이구나~

      

- 장점:

  - 직접접근이 가능함
  - 포인터 유실되어도 FAT에 정보가 있음 => 그래서 중간에 잘못되어도 접근가능







