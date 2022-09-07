# 영상 분석(Video Analysis)

- object detection

- object tracking

- action classification

Object탐지를 먼저함 => tracking => action을 분류하게 됨

### Object Tracking

- Video Stream : 실시간 영상

- Video Sequence : 업로드 영상

#### DeepSORT 이해하기

###### 칼만 필터 - 더 알아보기

- 이전 프레임에 등장한 개체를 이용 => 다음 프레임의 개체의 위치를 예측

- 예측한 값과 실제 측정값을 비교 => 더 잘 추측하기 위해 상태를 업데이트 하는 것

- 사용 이유
  
  - Detection 중 발생되는 Noise를 처리하는데 도움을 준다
  
  - 영상에서의 tracking은 선형성을 나타냄 

- 칼만 필터 state - Bounding Box
  
  - bbox 위치 + 각 요소의 속도 (vx,vy,va,vh)

[deep_sort/kalman_filter.py at master · nwojke/deep_sort · GitHub](https://github.com/nwojke/deep_sort/blob/master/deep_sort/kalman_filter.py)



###### Hungarian algorithm

칼만필터에서 이전 프레임과 다음프레임에서 발견된 새체가 동일하다는 것을 어떻게 판별???

- 최적의 매칭을 찾는 알고리즘

- 다수의 공급처와 수요처가 존재할 때 수송비용이 모두 다를때, 총 수송비용의 합이 최소가 되는 최적해를 찾는 것이 바로 할당 문제 => 이 할당문제를 해결하는 것



###### Mahalanobis distance

- 평균과의 거리가 표준편차의 몇 배인지를 나타내는 값
  
  - 즉 얼마나 일어나기 힘든 값인지 수치화 하는 방법
  
  - ex) 매일 20대만 지나감 => 내일 21대지나갈 확률 작음 => Mahalanobis distance 값이 매우 높을 것



###### SORT(Simple Online and Realtime Tracking)

-  실시간 추적을 위해 object들을 효율적으로 연관지어주는 MOT(Multi Object Tracking)

- MOT
  
  - detection 결과 간 연관(association)을 수행하는 과정

-  Online Tracking
  
  - 미래 프레임에 대한 정보 없이 과거와 현재 프레임의 객체 detection 정보만을 사용하여 연관 관계에 대한 Tracking을 수행하는 방식





![](video%20classificaton.assets/2022-09-05-15-30-35-image.png)

- Detection
  
  - 대부분 YOLO를 사용
  
  - better detection(더 좋은 객체 탐지) == better tracking(더 좋은 트래킹)



- Estimation
  
  - Kalman filter를 통해 개체를 추적하기 위한 측정치를 예측
  
  - 예측 값과 실제 측정치를 통해 업데이트 => 다음 프레임 값과 다시 IOU값을 측정 하는 재귀 필터 형태를 보임 (반복)



- Data Assosiation
  
  - unmatched Track / unmatched detection / matched track 이렇게 3개로 어떻게 나누는 것일까??
  
  - 할당에 관한 분기처리 => Hungarian algorithm을 사용
  
  - IOU를 Metric으로 사용
  
  - IoU 유사도 구함 => 추적되고 있던 개체와 아닌개체를 분류
  
  - 추적되고 있지 않던 개체
    
    - 사라진 개체
    
    - 새로 등장한 개체
  
  - 추적중인 개체는 Kalman filter를 통해 다음 개체를 추적하기 위한 측정치 업데이트
  
  - target overlap을 detection값이 IOU(min)보다 작은 값들은 할당문제에서 거절하게 된다
    
    - 



###### 칼만 fileter의 한계

Kalman filter가 뛰어나긴 하지만, 실제 상황에서 발생하는 Occulusion이나 Different View Point, ID switching 에는 불안정합니다.

Occulusion : 

- 개체가 어떤 상황에서 가려진 현상 => 중간에 트랙킹을 할 수없을떄 다른 ID값을 가지게 된다.



ID switching

- 다양한 개체가 움직일 때 ID의 추적이 변경될 수 있다는 점

- 개체의 특성을 파악해두면 Id를 구별하는데 효과적

- Different View Point 또한 비슷한 맥락으로 이해



#### DeepSORT

![](video%20classificaton.assets/2022-09-05-16-08-06-image.png)

![](video%20classificaton.assets/2022-09-05-16-08-55-image.png)

만약에 객체가 사라지거나 급격하게 변함 => 칼만 필터로 안됨 측정할 수 없음 => Deep Learning으로 각각의 객체 학습 => ID값 부여 => 다음부터 비슷하다고 생각되면 없어도 객체 Detection





Matching Cascade

- Detections와 Tracks사이의 cost matrix계산
  
  - 마할라노비스 거리와 코사인 거리의 가중 평균으로 cost matrix를 구하고 matrix가 너무 커지지 않도록 gate matrix를 이용
  
  -  Cosine을 이용하는 이유는 kalman fiter는 추정치를 제공하는 것이므로 이 외에 것을 설명하기 위해 사용한다
  
  -  Appearance Descriptor를 Cosine Distance를 의미

![](video%20classificaton.assets/2022-09-05-16-57-10-image.png)





Cosine Distance

-  Bounding box detection에 대해 절대값이 1인 Appearance Descriptor(ReID)
   Kalman filter로 얻는 예측 상태 분포는 객체 위치에 대한 대략적인 추정치만 제공하기 때문에, Kalman filter만으로는 설명되지 않는 모션들을 위해 Cosine Distance 도입합니다.



IOU Matching

- Unmatched Tracks, Unmatched Detections, Matched Tracks를 구분한다.

- IOU Matching을 다시 진행하는 과정을 거친다
  
  - 이유 : appearance chnage를 구하는데 도움을 준다
  
  - 부분적인 occlusions문제를 해결



Matching Result

- **Matched Tracks** : 
  
  - 계속해서 추적 중인 개체입니다. 이어서 Kalman filter를 Update합니다.

- **Unmatched Detections** : 
  
  - 새롭게 등장한 개체입니다. 새로운 Track으로 개체를 정의하지만 Tentitive(임시)상태로 구별하였다가 3번 등장할 때 Confirmed로 변경됩니다.

- **Unmatched Tracks** : 
  
  - 추적되던 개체를 발견하지 못했을 때입니다. 개체 추적이 안된다면 바로 삭제하는 게 아니고 다시 나타날 가능성이 있기 때문에 tentative 상태를 가지고 time_since_update 변수를 사용해서 상태를 지켜봅니다. 
  
  - 만약, 일정 기간 동안 (time_since_update>max_age) 발견되지 않는다면 Track 에서 제외됩니다.
  
  - 다시 등장하게 된다면, time_since_update를 0으로 초기화 시키고 다시 추적 상태로 돌아갑니다.
  
  
  
  ![](video%20classificaton.assets/2022-09-05-17-11-07-image.png)
































