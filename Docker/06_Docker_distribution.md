# 06_Docker_distribution





- Dockerfile : 개발단계, 실제 배포 후를 위한 단계로 나누어서 작성하는 것이 좋다.
  - **Dev Dockerfile.dev**
  - Prod Dockerfile



- dockerfile.dev로 만들경우 자동으로 dockerfile을 찾지 못한다.

```dockerfile
docker build -f Dockerfile.dev ./
이런식으로 이름을 설정해주어야 error를 피할 수 있다.
-f : 이미지를 빌드할때 쓰일 도커 파일을 임의로 지정해주는 것
```



```dockerfile
docker run -it -p 3000:3000 <이미지 이름>
```

- -it 를 하지 않으면 동작이 바로 빠져나가게 된다.



Volumne이용하기 



docker run --rm -it -p 3000:3000 -v /usr/src/app/node_modules -v %cd%:/usr/src/app soxn3579/docker-react

docker build -f Dockerfile.dev -t rkaehdaos/react1 .



```dockerfile
version: "3"
services:
  react:
    build:
      context: . # 도커 이미지를 구성하기 위한 파일들과 폴더의 위치
      dockerfile: Dockerfile.dev # 
    ports:
      - "3000:3000"
    volumes: # volume설정
     - /usr/src/app/node_modules
     - ./:/isr/src/app
    stdin_open: true    

```







