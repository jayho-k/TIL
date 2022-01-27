# Object Detection

- Classification(Single)
  - 정통적인 분류모델 방법
- Classification + Localization(Single objects)
  - 
- Object Detection (Multiple objects)
  - 대상의 개수가 여러개
- instance Segmentation
  - 각각의 픽셀로 구분을 한다



##  Object Detection

### 2-stage Detector

- 위치를 찾는 문제(localization) 해결 ==> 분류(classification) 을 순차적으로 진행

  1.  Region proposals (위치에 대한 정보를 제한한다.)

  2.  각각의 위치에 대해서 feature를 추출함 (extractor)
  3. Classification , Regression(바운딩 박스의 좌표를 예측하는 문제)

![image-20220122200501560](C:/Users/KBK/AppData/Roaming/Typora/typora-user-images/image-20220122200501560.png)

 R-CNN : 

1. 위치를 먼저 찾게 된다.
2.  cnn네트워크에 넣음 --> feature factor를 추출하게 된다.
3. SVMs를 이용해서 Classification을 진행
4. Regressors 를 이용해서 정확한 위치가 어디인지 bounding 박스를 조절해서 에측



 Fast R-CNN :

- 속도적인 면을 향상시킴

- R-CNN 과 다른점은 feature map을 뽑기위해서 CNN을 한번만 거치게 된다.
- softmax를 사용하게 된다



 Faster R-CNN :

- GPU상황에서 모델을 돌리게 된다
- Selevtive search를 Region Proposal Network(RPN)으로 대체
  - feature map을 보고 어느곳에 물체가 있을법한지 예측할 수 있도록 한다.
  - selective search에 대한 시간을 단축하기 위한 대안

![image-20220122201457824](C:/Users/KBK/AppData/Roaming/Typora/typora-user-images/image-20220122201457824.png)



### Region Proposal(물체가 있을 법한 위치 찾기) 

#### sliding window

![image-20220122201802124](C:/Users/KBK/AppData/Roaming/Typora/typora-user-images/image-20220122201802124.png)

- 너무 많은 영역에 대하여 확인 해야함
- 따라서 속도가 느리다는 단점을 가지고 있음



#### selective Search

- 인접한 영역(Region)끼리 유사성을 측정해 큰 영역으로차례대로 통합해 나간다.
- cpu기반 ==> 따라서 사진한장당 2초가량 시간이 걸릴수 있음

![image-20220122202343788](C:/Users/KBK/AppData/Roaming/Typora/typora-user-images/image-20220122202343788.png)



### 객체 검출(object Detection) 정확도 측정 방법

![image-20220122202554960](C:/Users/KBK/AppData/Roaming/Typora/typora-user-images/image-20220122202554960.png)

TP : 사물이 존재 + 정답을 맞춤

FN: 사물이 존재 + 오답(없다고 판단)

FP : 사물이 없음 + 오답(있다고 판단)

TN: 사물이 없음 + 정답을 맞춤

​         T는 정답을 맞춤 // F는 정답을 못 맞춤



- Precision(정확도)
  - TP / (TP + FP)   ==> 물체가 있다고 **판단 한 것들 중** // 정답을 맞춘 비율



- Recall (재현율) 
  - TP / (TP + FN)  ==>  물체가 **실제로** 있는 것들 중 // 정답을 맞춘 비율



ex) 강아지 20마리 // 모델이 10마리의 강아지를 검출 // 5마리를 맞춤

​       정확도 :  5/10마리 ==> 50%      재현율:  5마리/20마리  ==> 25%

ex) 강아지 10마리 // 모델이 20마리의 강아지를 검출 // 7마리를 맞춤 (더 많은 강아지 검출)

​	  정확도 :  7/20마리 ==> 35%      재현율:  7마리/10마리  ==> 70%



의미: 

- 막무가내로 모든 곳에 강아지가 있다고 판단 ==> 재현율 높음// 정확도 떨어짐
- 매우 확실할때만 강아지가 있다고 판다 ==> 재현율 떨어짐// 정확도 높아짐



### Average Precision

- 보통 정확도, 재현율은 반비례 관계
- 따라서 Average Precision으로 성능을 평가함 (단조감소 그래프로 넓이를 계산하게 된다.)

![image-20220122204639180](C:/Users/KBK/AppData/Roaming/Typora/typora-user-images/image-20220122204639180.png)



### Intersection over Union (IoU) 교집합 / 합집합

- 그럼 어떻게 FP, TP인지 알수 있을까?  IoU를 이용하게 된다
- 검출한 바운딩 박스가 실제 바운딩 박스와 얼마나 유사한지 판가름 하는 척도
- IoU : 두 바운딩 박스가 겹치는 비율을 의미
- 활용방식
  - 성능 평가: mAP@0.5: IoU가 50%이상일때 정답으로 판단
  - NMS 계산: 같은 클라스 끼리 IoU가 50%이상 ==> 낮은 confidence의 박스 제거

![image-20220122205508395](../AppData/Roaming/Typora/typora-user-images/image-20220122205508395.png)

즉 얼마만큼 겹치고 있니? 를 물어보는 것이다.



### NMS (Non Maximum Suppression)

- 제일 큰 것을 제외하고 나머지는 업축을 해버리자!! 라는 의미이다.
- 하나의 instance(대상)에 하나의 bounding box가 적용되어야 한다. 
- 따라서 여러개 bounding box ==> 하나로 합침

![image-20220122211411036](../AppData/Roaming/Typora/typora-user-images/image-20220122211411036.png)









## 논문 확인하기

### 1. R-CNN: Region with CNN features

- Selective Search이용 ==> 2000개의 Region Proposal을 생성 
  - 각 Region Proposal을 일일이 CNN에 넣어서 forward 결과를 계산

![image-20220122211808925](../AppData/Roaming/Typora/typora-user-images/image-20220122211808925.png)

- 동일한 너비와 높이 크기의 이미지를 넣게 된다.

![image-20220122211929250](../AppData/Roaming/Typora/typora-user-images/image-20220122211929250.png)

1. 물체가 존재 할법한 위치를 찾아낸다.
2. 크기를 동일하게 잘라낸다
3. 각각의 CNN기반의 feature 리스틱(?)에 넣고 feature vector를 뽑는다
4. binary SVM에 넣어서 어떤 클래스에 해당하는지 계산
5. Bbox reg모델을 사용해 어떤 위치에 존재하는지 더 정확히 계산하게 된다.

![image-20220122212534283](../AppData/Roaming/Typora/typora-user-images/image-20220122212534283.png)

- RoI : region proposal과 같은 의미이다.



#### bounding box regression

-  지역화(localization) 성능을 높이기 위해 bounding box regression을 사용

![image-20220122214312900](../AppData/Roaming/Typora/typora-user-images/image-20220122214312900.png)

- 예측 위치 : selective search를 하면 물체가 존재할 법한 예측 위치가 나옴 
- 실제 위치 : 실제 존재하는 위치를 데이터에서 가져온다.

- 학습 데이터셋 : (예측위치 , 실제 위치)
  - 예측된 위치 정보가 주어졌을 때 실제 위치와 비교하여 조정을 시켜줘야 함
- 4개의 값을 예측하도록 해야함 : (Px,Py): 중앙 위치값, Pw: 박스 너브 , Ph:박스 높이
- RCNN은 4개의 Parameter를 학습시킴(얼마나 차이가 나는지)
-  ==> Linear regression을 진행하게 됨

![image-20220122214921865](../AppData/Roaming/Typora/typora-user-images/image-20220122214921865.png)



#### R-CNN의 한계점

- cpu 기반 ==> 시간이 오래걸림

- CNN은 고정 vm, bouding box regression까지 forwarding을 한 뒤
  CNN은 feature restrictor(?)까지 추출할 수 없음

  - CNN은 feature만 따로 추출함

  - svm, bouding box regression모듈은 따로 동작함
  - 즉 end to end 방식으로 학습할 수 없다

- 모든 Rol를 CNN에 넣어야 한다.  ==> 200번의 CNN계산이 필요하다
  - 학습과 평가 과정에서 많은 시간이 필요하다



### 2. Fast R-CNN

- 가장 큰 차이점: 
  - 이미지를 한번만 CNN에 넣는다
  - svm을 사용하지 않는다 ==> softmax를 사용하게 된다
- 정확한 위치를 찾아내기 위해서 regression 모델을 사용하게 된다.

![image-20220122221653130](../AppData/Roaming/Typora/typora-user-images/image-20220122221653130.png)



#### RoI Pooling Layer(가장 핵심이 되는 내용)

![image-20220122222059009](../AppData/Roaming/Typora/typora-user-images/image-20220122222059009.png)

- 고정된 크기의 feature 벡터를 생성해야한다.
- max pooling을 활용하게 된다
- 2x2의 maxpooling라면 적절하게 2x2로 나누어 지게끔 만들어준다 (2개 행, 2개 열)
- 이렇게 하면 항상 고정된 feature vector의 값을 얻을 수 있다.



### 3. Faster R-CNN

핵심 : region proposal network(RPN) --> gpu에서 사용할 수 있도록 만든 것임

- 전체 아키텍처를 end to end로 학습이 가능하다
- rpn, detector network 둘다 이미지에 대해서 처리를 수행
  - 따라서 앞쪽에서 feature map을 뽑아내는 feature restrictor를 고융할 수 있음

1. 입력 이미지
2. vgg(?)기반 네트워크로 특징 추출 
3. 그렇게 얻은 feature map을 이용해서 RPN은 물체가 있을법한 곳을 찾음
4. detector한테 여기 물체 있을 것 같다고 알려준다. 
5. 그렇게 얻은 정보를 통하여서 분류를 하게된다.

![image-20220122222842350](../AppData/Roaming/Typora/typora-user-images/image-20220122222842350.png)



### RPN의 동작방법

- feature map이 주어졌을 때 물체가 있을 법한 위치를 예측하게 된다. 
  - k개의 서로다른 앵커박스(anchor box)를 사용하게 된다
    (다양한 크기의 사물을 예측하기 위해서)
  - 슬라이딩 윈도우를 거쳐 regression과 classification을 수행하게 된다.

![image-20220122224905158](../AppData/Roaming/Typora/typora-user-images/image-20220122224905158.png)

1. feature map에서 왼쪽 위부터 오른쪽 아래까지 슬라이딩 윈도우를 이용
2. 각 위치에대해서 intermidiate feature를 뽑음
3.  regression 과 classification 을 진행하게 된다. 

- RPN은 단순히 있을 법한 위치를 판단하기 위한 것
  - 따라서 물체가 있는지 없는지에 대한 여부만 판단하게 된다.
  - regression layer를 거쳐 bounding 박스의 중간점, 너비 높이 값을 예측하도록 함





















### 1-stage Detector

- 위치를 찾는 문제(localization) + 분류(classification) 을 한번에 진행
- 2stage보다 빠르다 but 정확도는 떨어진다.
- 





























