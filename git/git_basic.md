# git



## Interface

GUI( Graphic User Interface): 컴퓨터와 유저의 상호작용

CLI(command line interface): 컴퓨터만의 언어



## 경로

- ~/ 주소: 내 위치

- 상대경로: 내 위치에 따라서 접근하는 곳이 바뀔 수 있다. 

- 절대경로: 어디서 접근하던지 변하지 않는다.

  

## 초기 세팅

git config --global user.name {유저이름}

git config --global user.email{이메일}

git config --global -l : 확인하는 용도



### 새로운 디렉토리 순서

순서: touch ==> add ==> commit

순서: git remote add origin {주소}:  ==> git remote -v ==> touch ==> add ==> commit 

​		==> git push -u origin master

연결 ==> 버전 ==> 파일 ==> 추가 ==> 커밋 ==> 올리기



## 문법

### 기본 문법

- **mkdir** :

  - 폴더 만들기
  - 

- **ls** : (list segment) :

  -  폴더들을 보여주게 된다.
  -  ls -a : 모든 폴더들을 보여주게 된다.
  -  ls --all: 숨김파일도 보여주게 된다.

  

- **cd**

  - cd : change directory : folder1으로 이동하는 것

  - cd + 띄어 .. :  부모 디렉토리로 옮길꺼야

  - .. : 부모 디렉토리를 가르킨다

  - . : 현재 디렉토리로 가르킨다

    

- **touch**

  - touch: 파일을 생성 ==> 확장자까지 써줘야한다 ex) a.txt

    

- **start**

  -  실행 ex) start a.txt

    

- **mv**

  - mv 파일이름1 파일이름2: 파일이름을 변경시키는 것

  - mv 파일이름 폴더 : 파일이름을 폴더이름으로 옮길꺼야

    

- **rm**

  - rm 파일이름.txt : 파일을 지우기 방법

  - rm *.txt :              txt를 모두 지워라는 뜻이다.

  - rm - r folder1:     폴더를 지우는 방법

  - rm - r f folder1:   init되어있는 폴더 지우기

    

### 깃 문법

- **git init**: 

  - 깃을 시작한다

    

- **git status: **

  - 깃의 상태를 확인 할께

    

- **git add**

  - git add a.txt:  깃에다가 a.txt 파일을 더할께 --> 깃을 statge area에 보낼께

  - git add . :         이 폴더에 있는 모든 애들을 추가하겠어

    

- **git commit -m "first commit"**: 

  - 메세지 first commit을 남기겠어

  - git commit만 쳤을때 메모장으로 들어와진다

    빠져나오는 방법 == i를 누른다 ==> esx ==> :wq ==> git log --oneline

- **git log:** 

  - commit에 어떤 파일이 있는지 말해준다

  - git log --online: 코밋 상태를 한줄로 확인한다

    

- **git remote**

  - git remote add origin {주소}:  
    - 깃허브로 연결을 하는 것 (주소는 깃허브 홈페이지에서 가져온다)
  - git remote -v
    - 연결되었는지 확인

  - git remote rm origin

    - 제거하는 방법

    

- **git push origin master : **

  - origin(별명)이라는 mater에 올릴꺼야

  - git puch -u origin master: origin master를 기억해준다 (origin master를 치기 귀찮음)

    

### 불러오기

### clone

- git clone {url} : 복사해 오는 것
  - git hub를 통해서 협업 가능//
  - 깃이 아닌 상태에서 깃허브의 레포지토리(저장소)를 복사해오는 것
  - 이때는 폴더와 함께 복사를 해온다. (이름이 그래로)
- git clone {url} . : git 자체를 복사해 오는 것
  - 따라서 이름이 본인이 만든 폴더에 복사를 해오게 된다.
- git clone {url}.git prac3:
  - prac3폴더 만들고 복사

### 동기화 (update):  git pull

- clone 이후 ==> git pull ==> 그대로 바로 update를 할 수 있다. 
- 원본에서만 올리고 내릴수 있는 것 x // 클론에서도 가능



### branch 만들기

- git.branch: 가지를 만들게 된다.

- git.switch {이름}: 이동하기
- git branch -d {name}: branch 를 지우게 된다.
- 마스터에서 합쳐야함
- git merge {branch} : branch를 합칠께

- 



# 깃 저장공간



**로컬 저장소(git)**

- wordking directory

- commit :  버전을 넘기는 용도 (커밋에 올린다)

- staging area: 올리기 전에 임시로 저장하는 것



**깃에서 하지말아야 할 것**

1. home_dir 에서 깃 시작하지 않기

   ( 다른 어떤 위치에서도 깃을 시작할 수 없게 된다.)(관리해야할 것이 너무 많아짐) 등등

2. 깃에서 깃시작하지 않기 (버전관리가 지워지기 때문이다)



실제폴더 == 실제폴더 + 로컬 저장소(git)









### 충돌났을 때 오류

 ! [rejected]        master -> master (fetch first)
error: 레퍼런스를 'https://github.com/holawan/TIL.git'에 푸시하는데 실패했습니다
힌트: 리모트에 로컬에 없는 사항이 들어 있으므로 업데이트가
힌트: 거부되었습니다. 이 상황은 보통 또 다른 저장소에서 같은
힌트: 저장소로 푸시할 때 발생합니다.  푸시하기 전에
힌트: ('git pull ...' 등 명령으로) 리모트 변경 사항을 먼저
힌트: 포함해야 합니다.
힌트: 자세한 정보는 'git push --help'의 "Note about fast-forwards' 부분을
힌트: 참고하십시오.

- 해결방법: pull을 새로하고 다시 올리셈
- git status ==> both modified {파일}이 뜨게 됨 ==> 판단을 해줘야 함



### 중요한 점 

- 같은 폴더, 다른 파일 ==> 충돌이 일어나지 않음
- 같은 파일 ==> 충돌

