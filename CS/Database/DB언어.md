# DB언어

> - DB에서는 모든 작업을 SQL문으로 작업
>
> - SQL문은 다루는 **객체나 용도에 따라 그룹핑**하여 나눌수 있다.
>   - 즉 **명령어를 구분**해 놓은 것



#### DDL

> Data Definition Language : **데이터 정의어**
>
> 데이터의 구조를 정의하는 데 사용하는 명령어 (생성, 변경, 삭제, 이름변경)등을 하기 위한 명령어

- create  : 테이블 생성
- alter     : 테이블 수정
- drop     : 테이블 삭제
- rename: 테이블 이름 변경
- truncate: 테이블 안에 있는 데이터를 전체 삭제



#### DML

> Data Manipulation Language : **데이터 조작어**
>
> DB안에 있는 데이터를 조회하거나 데이터에 변형을 할 수 있는 명령어입니다.

- Select    : 데이터를 검색한다.
- Insert    :  데이터를 생성한다.
- Update : 데이터를 수정한다.
- Delete   : 데이터를 지운다.



#### DCL

> Data Control Language : **데이터 제어어**
>
>  DB에 접근하고 객체들을 사용할 수 있도록 하는 권한을 주고 회수하는 명령어입니다.

- Grant - 권한을 부여한다.
- Revoke - 권한을 회수한다.



#### TCL

> Transaction Control Language : **트랜젝션 제어어**

- Commit - 변경된 데이터를 테이블에 영구적으로 반영한다.
- Rollback - 데이터 변경을 취소하여 데이터를 이전 상태로 복구한다.
- Savepoint - 롤백은 이전의 데이터 변경을 취소한다면 savepoint는 저장 위치를 정의한 곳까지 돌아간다.

