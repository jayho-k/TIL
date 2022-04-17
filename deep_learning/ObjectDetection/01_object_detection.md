# 01_object_detection



## Object_detection and Segmetation??

#### Localization 

- 하나의 이미지 안에서 딱 하나의 Object만 detection하는 경우

- bounding box로 지정하여 찾음

- ##### 순서

  - Object위치를 bounding box로 먼저 찾음
  - bounding box내의 Object를 판별

- ##### 특징

  - bounding box regression(연속된 값)
  - 즉 ( box의 좌표값을 예측하는 것 )
  - 그리고 classification을 하는 것



#### object_detection

- Image = 1 ,  Object = n

- bounding box로 detect 하는 것

- ##### 순서

  - Object위치를 bounding box로 먼저 찾음
  - bounding box내의 Object를 판별

- ##### 특징

  - bounding box regression(연속된 값)
    - 즉 ( box의 좌표값을 예측하는 것 )
  - 그리고 classification을 하는 것
  - Localization과 달리 여러개의 object를 찾아야함 ==> 어려움이 있음



#### segmentation

- bounding box로 detect (X)  ==> 픽셀단위로 detection 함



## Stage

#### one - stage

- 한번에 detection함

- 특징
  - 속도가 빠름
  - 정확도도 높아지게 됨
- ex)
  - YOLO계열, SSD, Retina-Net



#### Two-stage

- 있음직한 곳을 먼저 찾고 분류 시작

- 특징

  - 정확성 높음

  - 느림
    - 먼저 있음직한 부분을 찾고 => 그것을 또 분류해야함

- ex)

  - RCNN 계열



## Object Detection

#### 구성 요소

1. ##### Region Proposal

   - object가 있음직한 곳을 찾는 것 ==> 힌트
   - 그리고 나서 bounding box를 친다

2. ##### Detection을 위한 deep learning network 구성

   - Feature Extraction(backborn)
     - 이미지에서 중요한 부분들을 뽑아 낸다라는 의미
     - Feature map을 만든다(크기 감소, 채널수 증가)
   - FPN(Feature Pyrimid Network) (neck)
   - Network Prediction(head )

3. ##### Detection을 구성하는 기타 요소

   - IOU
   - NMS
   - mAP
   - Anchor box



###  Object Detection이 어려운 이유

- ##### Classification  + Regression을 동시에 가능해야 함

  - Loss가 두개 다 좋아야함
  - 둘다 최적화가 다 좋아야함
  - 따라서 복잡해진다



- ##### 다양한 크기와 유형의 object가 섞여 있음

  - box의 모양이 각각의 다르다
    - ex) 자동차 가로로 긴 박스 , 사람 세로로 긴 박스



- ##### Detect가 빨리 되어야한다

  - 정확성 높음? ==> 복잡 ==> 시간 오래걸림
  - 시간 줄임 ==> 단순? ==> 정확성 떨어짐
  - 망함



- 명확하지 않은 이미지
  - 이미지 내에 background가 차지하는 경우가 높음
    - 그럼 background는 넘어가주어야하는데 안 그런경우가 많음



- 훈련가능한 데이터 세트 부족
  - 왜??
    - annotation을 만들어야 한다.
    - annotation?
      - 정답을 만들어 주는 것
      - 라벨링 => 네모 겁나 쳐야함 => 수작업 => 귀찮 => 데이터 부족



## Object Localization개요

- ### 다시(4분)

annotation 파일에 Bounding box에 대한 좌표값을 가지고 있음

- (x,y) * 2
- feature map에서 Bounding nox Regression layer가 따로 나옴
  - Bounding nox Regression => 있음직한 곳을 찾는 것 
- 어차피 물체 하나 ==> 그래서 그때 그때마다 regression해주면 된다.



## Object Detection

- 여러개의 object가 있어야함
- feature map에 여러가지 object가 있다는 뜻



#### 있음직한 곳을 왜 먼저 찾는 것일까??

- 안할 경우 => 예측을 엉뚱한 곳에 하게 됨
- 일단 이미지가 굉장히 많음
- 이런 feature일 때는 이렇게 detect하면 되겠구나 라고 함
- 근데 사람이 많음 ==> 사람이 다 똑같아 보임
- 그럼? ==> 1번 째 이미지일땐 오른쪽 ==> 2번 째 이미지일떈 왼쪽??
- 아니 내가 보기엔 둘다 똑같길래 ==> 그냥 아무곳에다가 박스침
- 그래서 있을만한 곳을 먼저 찾아주는 것임
  - 비유:
    - 이탈리아를 감
    - 사람이 다 똑같이 생김
    - 알렉스(수염 + 안경)를 찾아야하는데 이사람도 알렉스 저 사람도 알렉스인거 같음
    - 자! 오키 ==> ㄱㄷ ==> 알렉스 내가 보기에 오른쪽 건물 안에 있는 거 같음 거기서 찾아보셈
    - 보니깐 어? 알렉스랑 맞는 거 같음

























