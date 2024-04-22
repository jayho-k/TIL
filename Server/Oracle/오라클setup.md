# 오라클 setup



오라클은 tnsname을 가지고 오라클 DB서버를 인식을 하는 것

- tns 설정
  - Net Configuration Assistant 프로그램으로 만들면 편함
  - 로컬 네트 서비스 이름 구성
  - 추가
  - 서비스 이름
    - default는  ==> GLOBAL DB NAME
    - GLOBAL DB NAME이랑 똑같이 가면 된다.
  - TCP
  - 호스트 이름 : IP:PORT번호로 진행
  - 사용자, 암호 
  - 네트 서비스 이름 : client에서 이 서비스를 인식하는 것
  - CMD
    - sqlplus
      - sqlplus system@OLCS
      - 이렇게 하면 서버에 접속이 된다.
      - 확인 : SELECT INSTANCE_NAME FROM V$INSTANCE































