

# 05Authentication





![image-20220411091852158](05Authentication.assets/image-20220411091852158.png)







HTTP vs HTTPS

HTTPS ==> + security 가 추가된 느낌으로 알고 있자



HTTP특징

- 비연결지향( 서버와 클라이언트는 연결되어 있는 것이 아니다 )
- 무상태
  - ( 정보가 유지 되지 않음 )
  - 즉 클라이언트와 서버가 주고 받는 메시지들은 서로 완전히 독립
- 즉! 지속적인 관계를 유지하기 위해 쿠키와 세션이 존재한다.



### 쿠키 개념

- 서버가 브라우저에 전송 ==> 작은 데이터 조각



#### 역할

- 클라이언트가 매 요청마다 쿠키를 보냄
- 즉 나 로그인 되어 있는 사람이야!! 라고 쿠키와 함께 요청을 보내는 것
- 왜? ==> 연결되어있지 않기 때문에



#### 개념

- HTTP 쿠키는 상태가 있는 세션을 만들어 준다
- 쿠키는 두 요청이 동일한 브라우저에서 들어왔는지 아닌지를 판단할 때 주로 사용한다.
  - 로그인 상태 유지 가능
  - 상태 전보를 기억 시켜준다
- 순서
  - 웹 페이지에 들어감
  - 쿠키 받음, 저장
  - 클라이언트가 같은 서버에 재요청시 쿠키를 같이 보냄



#### 목적

- 세션관리
  - 로그인, 아이디 자동완성, 팝업 체크, 장바구니 등등
- 개인화
  - 사용자 선호, 테마 등의 설정
- 트래킹
  - 사용자 행동을 기록 및 분석



##### ex) 장바구니

- ##### 장바구니에 물품을 넣게 되면 쿠키에 정보가 담겨 간다

  - 물품을 추천해줄 때 이것을 이용함

- ##### 그럼 장바구니에 물품을 지운다?

  - 쿠키를 지우는 것
  - 물품을 추천해주지 않음



### 세션(Session)

#### 순서

- 클라이언트 => 서버 접속 ==> session id를 발급
- session id를 쿠키에 저장
  - 다시 서버 접속 ==> 쿠키안에 session id를 넣음 ==> 서버에 전달
  - ID는 세션을 구별하기 위해 필요하며, 쿠키에는 ID만 저장함



역할

- 사용자가 권한이 있는지를 계속해서 확인할 수 있게 해준다
- 로그 아웃 ==> 세션을 삭제하는 과정이었다
- 즉 세션을 삭제하면 자연스럽게 로그아웃이 된다
  - 왜?? ID를 가지고 있지 않아 서버에서 거절하게 된다



쿠키 lifetime

1. Session cookies

   - 현재 세션이 종료되면 삭제 됨( 세션 주기가 끝나면 )

   - 일부 브라우저는 다시 시작할 때 세션 복원 ==> 오래 지속가능하게 한다

2. Persistent Cookies

   - Expires 속성에 지정된 날짜 혹은 Max-Age 속성에 지정되 기간이 지나면 삭제
   - 즉 창을 꺼도 로그아웃이 되지 않는다
   - 일정시간이 지나면 로그아웃



### Session in Django

- Django에서 세션은 미들웨어를 통해 구현됨



- SessionMidleware
  - 요청 전방에 걸쳐 세션을 관리
- AthenticationMiddleware
  - 세션을 사용하여 사용자를 요청과 연경





## 로그인

#### 로그인이란?

- 세션을 Create하는 로직과 같음



##### Authentication Form

- 사용자 로그인을 위한 form
- request를 첫번째 인자로 취함



##### login 함수

- user의 ID를 저장한다 (세션에) 

- 인증을 받을 때만 보거나 접근할 수 있게 만들어주는 방법 2가지

  1. is_authenticated

  2. @login_reqiured

![image-20220411164512993](05Authentication.assets/image-20220411164512993.png)

![image-20220411164726931](05Authentication.assets/image-20220411164726931.png)



## Authentication data in templates

![image-20220411164943626](05Authentication.assets/image-20220411164943626.png)





## Logout





## 회원가입

- username
- password 1
- password 2

![image-20220411143915057](05Authentication.assets/image-20220411143915057.png)

![image-20220411143929887](05Authentication.assets/image-20220411143929887.png)







## 회원탈퇴

![image-20220411144841458](05Authentication.assets/image-20220411144841458.png)

![image-20220411144903325](05Authentication.assets/image-20220411144903325.png)





## 회원 수정





## 비밀번호 변경





