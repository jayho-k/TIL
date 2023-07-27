# 04_ModelServing

https://velog.io/@khs0415p/MLOps-Serving



## 01) Model Serving이란

- Production( real world )환경에 모델을 사용할 수 있도록 배포하는 것
- 서비스 하는 것
- 종류
  - Online
  - Batch
  - Edge

## 02) Online Serving

> - request가 올 떄마다 실시간으로 예측

### 02-1) 구현 방식

- API 웹 서버 개발
- 클라우드 서비스 활용
- Serving 라이브러리 활용

### 02-2) 고려해야할 점

- Depadency
- 지연시간(Latecy) 최소화
  - DB쿼리, 모델 경량화, 후처리



## 03) Batch Serving

> - 주기적으로 학습 (30분의 한번 등)
> - Airflow 등으로 스케쥴링 작업

**장점**

- OnlineSrerving 보다 구현이 수월하고 간단하다.
- Latency가 문제되지 않는다.

**단점**

- 오늘 새로생긴 컨텐츠 추천할 수 없음













Custom resource

- 쿠버네티스의 API확장판
  - 유저가 직접 정의한 리소스를 쿠버네티스의 API를 사용해서 관리하고 싶은 경우
  
  - 해당 CR의 LifeCycle과 동작을 관리할 Controller(API 서버)를 구현 후 쿠버네티스 클러스터에 배포
  
    
  
- CR을 클러스터에 등록하는 방법
  - Custom Resource Definition(CRD)
    - CR을 관리할 Custom Controller 를 구현하고 배포하여 사용
    - Controller는 대부분 Operator pattern으로 개발 된다.
  - API Aggregation (AA)







Operator Pattern

- Controller

  - Desired State(목표값)과 Current State(현재값)을 API호출 또는 주기마다 비교하여, Current State를 Desired State에 일치시키도록 지속적으로 동작하는 무한루프

    

- Operator

  - Controller Pattern을 사용하여 사용자의 애플리케이션을 자동화 하는것
  - 주로 CR 의 Current/Desired State 를 지속적으로 관찰하고 일치시키도록 동작하는 역할을 위해 사용



Helm

- 쿠버네티스 모듈의 Package Managing Tool
  - python 패키지 관리도구인 pip와 비슷한 역할
  - a.yaml, b.yaml 등 많은 수의 쿠버네티스 리소스 파일들을 모두 관리하기에 버전관리, 환경별 리소스 파일 관리 등이 힘들다.
- Helm은 이러한 작업을 템플릿화 시켜서 많은 수의 리소스들을 마치 하나의 리소스처럼 관리할 수 있게 도와주는 도구이다.
  - Helm manifest
    - `templates` : 모든 쿠버네티스 리소스들의 템플릿 파일이 보관된다.
    - `values.yaml` : values.yaml라는 인터페이스로부터 사용자에게 값을 입력받아 templates의 정보와 merge하여 배포된다.



