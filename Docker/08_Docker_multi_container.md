# 08_Docker_multi_container



## 복잡한 구조 (multi container)

> - 리액트, 노드, 데이터 베이스 구조를 활용하여 배포하기
> - 개발환경
> - 배포

![image-20230710222013357](C:\Users\jayho\Developer\practice\Docker\07_Docker_distribution2.assets\image-20230710222013357.png)



## Nginx의 Proxy를 이용한 설계

<img src="./08_Docker_multi_container.assets/image-20230710223328046.png" alt="image-20230710223328046" style="zoom:67%;" />

- 장점
  - Request를 보낼때 URL부분을 host이름이 바뀌어도 변경시켜주지 않아도 된다.
  - 포트가 바뀌어도 변경을 안해주어도 된다.
- 단점
  - nginx설정, 전체 설계가 복잡하다



### Dockerfile.dev

```dockerfile
FROM node:alpine

WORKDIR /app

COPY pakage.json ./

RUN npm install

COPY ./ ./

CMD [ "npm","run","start" ]
```



### Dockerfile

```dockerfile
FROM node:alpine as builder
WORKDIR /app
COPY pakage.json ./
RUN npm install
COPY ./ ./
RUN npm run build



FROM nginx
EXPOSE 3000 # port번호

# ./nginx/default.conf => 앞쪽 nginx는 proxy로 만들어 놓고 front쪽의 nginx를 뜻한다.
# /etc/nginx/conf.d/default.conf => container안에 있는 nginx폴더 안에 넣어준다는 뜻이다.
# 즉 default.conf파일을 container안에 copy한다는 뜻
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

#
COPY --from=builder /app/build  /usr/share/nginx/html 
```

```yaml
# default.conf
server {
    listen 3000; # 3000번 port 

	# location/ 이라고 url이 오면 {} 안에 있는 것들이 실행된다.
    location / {
        root /usr/share/nginx/html; # nginx 기본 파일(정적파일들 저장되어 있는 곳)
        index index.html index.htm; # react index파일 설정
        try_files $uri $uri/ /index/html; # react SPA이기 때문에 설정
    }
}
```





















