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



```yaml
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





## 도커를 이용해서 테스트 진행

```dockerfile
docker run -it <이미지 이름> npm run test
```



```yaml
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


    tests:
      build:
        context: .
        dockerfile: Dockerfile.dev
      volumes:
        - /usr/src/app/node_modules
        - ./:/usr/src/app
        command: ["npm","run","test"]
		
```

- docker-compose up --build





## Nginx : 운영환경

- 운영환경에 가면 개발서버가 없어진다.
- 즉 개발서버 대신에 Nginx가 정적파일들을 제공해주게 된다.
- 개발 서버를 운영서버로 사용하면 안되는 이유
  - 개발 서버 : 자동으로 전체 앱을 다시 빌드해서 변경소스를 반영해주는 것과 같이 개발환경에 특화된 기능들이 있기때문
  - Nginx : 개발에 필요한 기능들이 필요하지 않기에 더 깔끔하고 빠른 Nginx를 웹 서버로 사용한다.



**단계**

1. 빌드 파일 생성
2. Nginx 가동 => 빌드폴더의 파일들을 웹브라우저의 요청에 따라 제공

```dockerfile
# builder stage : 빌드파일 생성 => usr/src/app/build로 파일들이 들어간다.
FROM node:alpine as builder
WORKDIR 'usr/src/app'
COPY package.json .
RUN npm install
COPY ./ ./
RUN npm run build

# run stage 
FROM nginx # nginx 베이스 이미지
COPY --from=builder /usr/src/app/build /usr/share/nginx/html
```

- **--from =builder** : as builder에서 가져온다는 뜻
- builder stage에서 생성된 파일 +> **/usr/src/app/build**에 저장
- **/usr/src/app/build**에 저장된 팡일들을 **/usr/share/nginx/html**로 복사를 시켜줘서 nginx가 ㅇ웹 브라우저의 http 요청이 올때마다 알맞은 파일을 전해 줄 수 있게 만든다.
  - 저장해주는 경로는 임의로 만드는 것이 아니라 Dockerhub 공홈에 nginx에 대한 설명이 있다.



이미지 생성 했다면 그 이미지를 이용해서 앱 실행

```shell
# Nginx의 기본포트는 80이다.
docker run -p 8080:80 <이미지 이름>
```

















