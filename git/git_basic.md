## 깃 저장공간

실제 폴터 = git_init



 로컬 저장소(git)

- wordking directory

- commit :  버전을 넘기는 용도 (커밋에 올린다)

- staging area: 올리기 전에 임시로 저장하는 것



깃에서 하지말아야 할 것

1. home_dir 에서 깃 시작하지 않기

   ( 다른 어떤 위치에서도 깃을 시작할 수 없게 된다.)(관리해야할 것이 너무 많아짐) 등등

2. 깃에서 깃시작하지 않기 (버전관리가 지워지기 때문이다)



초기 세팅

git config --global user.name {유저이름}

git config --global user.email{이메일}

git config --global -l : 확인하는 용도



실제폴더 == 실제폴더 + 로컬 저장소(git)



새로운 디렉토리

순서: touch ==> add ==> commit



git 문법

- git init: 
  - 깃을 시작한다

- git status: 
  - 깃의 상태를 확인 할께

- git add a.txt: 
  - 깃에다가 a.txt 파일을 더할께 --> 깃을 statge area에 보낼께

- git add . : 
  - 이 폴더에 있는 모든 애들을 추가하겠어

- git commit -m "first commit": 

  - 메세지 first commit을 남기겠어

  - git commit만 쳤을때 메모장으로 들어와진다

    빠져나오는 방법 == i를 누른다 ==> esx ==> :wq ==> git log --oneline

- git log: 
  - commit에 어떤 파일이 있는지 말해준다
  - git log --online: 코밋 상태를 한줄로 확인한다

- rm *.txt :  
  - .txt를 모두 지워라는 뜻이다.

- git remote add origin {주소}:   (주소는 깃허브 홈페이지에서 가져온다)
  - 깃허브로 연결을 하는 것

- git remote -v
  - 연결되었는지 확인

- git remote rm origin

  - 제거하는 방법

- git puch origin master : origin(별명)이라는 mater에 올릴꺼야
  - git puch -u origin master: origin master를 기억해준다 (origin master를 치기 귀찮음)

- git commit만 쳤을때 메모장으로 들어와진다
  - 빠져나오는 방법 == i를 누른다 ==> esx ==> :wq ==> git log --oneline

- 

