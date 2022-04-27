# 04_SPP(Spatial Pyramid Pooling)_Net





## 00 R-CNN??

#### 문제점

- 2000개의 region영역 이미지가 CNN에 입력됨 ==> 시간이 오래걸림

- Region 영역 이미지가 Crop/Wrap되어야함 (늘려지고 줄여지고 등등) ==> 이미지가 이상해짐(손상)



#### 개선 방안

![image-20220425203626427](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425203626427.png)

- 그냥 원본 이미지를 Feature Extractor에 넣는다

- 그리고 SS에서 찾은 예측한 것들을 Feature map에 mapping하게 된다??????????????

- ##### 아쉽지만 안됨

  - 왜?
  - Flatten Fully Connection Input의 크기가 고정이 되어야 하기 때문이다.
    - 하지만 크기가 제각각이기 때문에 length가 커졌다가 작아졌다가 하게 된다.
  - 즉 네모 분홍색을 학습시켜야 하는데 Dense하게( 한줄로 )어떻게 만들어야 할지 모르는 것



#### 이것을 mapping할 수 있는 별도의 layer를 하나 만들자!!!

![image-20220425204451264](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425204451264.png)



## SPP

- input 이미지 사이즈를 고정시키지 말자
- 이미지 사이즈가 다양하게 들어옴

![image-20220425204803042](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425204803042.png)

- 이미지를 고정시켜서 conv layer에 넣어 줬어야 했음
- 하지만 그러지 말고 spatial pyramid pooling을 중간에 넣어주면 이미지 사이즈가 다양하더라도 Classification을 할때 문제가 없더라
- 이것은 Spatial pyramid Matching에 근간을 두고 있다



### Bag of visual words

![image-20220425210529280](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425210529280.png)

##### bag of words

- 문서가 어떤 문서인지 분류하기 위한 방법중 하나

-  EX) 

  - 기사를 뽑아 봤더니 => 농구, 공, 선수, 드리블 등의 단어가 많음 => 일단 집어 넣음
    ==> 그럼 농구구나? 스포츠 기사이겠구나? 라는 생각을 할 수 있음

- 이미지에도 이런 방법을 사용

- 영상처리, 컴퓨터 비전 쪽에서는 Bag of Words 기법을 주로 이미지를 분류(image categorization)하거나 검색(image retrieval)하기 위한 목적으로 사용하였는데, 최근에는 물체나 씬(scene)을 인식하기 용도로도 폭넓게 활용되고 있다. https://darkpgmr.tistory.com/125

  

##### 방법

- 특정 영역을 잘라서 그냥 집어넣음
- 그래서 많이 나오는 비슷한 특징들을 histogram으로 표현
  - 원본이 가지고 있는 정보들을 새로운 정보로 mapping하는 것이다
- 분류



##### 문제점

![image-20220425210935048](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425210935048.png)

- 문맥이 없어짐 ==> 따라서 정확성이 떨어지게 된다.
- 이미지도 똑같음 ==> 만약 바다 사진을 봤는데 모래가 많이 나옴 ==> 사막인가?
- 위치라는 개념이 필요함 ==> 어디에 뭐가 있는지
- 그래서 나온 개념 ==> SPM(Spatial Pyramid Matching)



### SPM(Spatial Pyramid Matching)



![image-20220425211039731](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425211039731.png)

- 구역을 나눠서 뭐가 얼마나 있는지를 확인하는 것
  - 즉 바다가 있으면 2/3지점에는 바다가 많다! 라는 문맥을 파악하는 것이다.
- 결과의 정보를 기준으로 무언가를 판단할 수 있게 된다. ==> 즉 분류를 할 수 있게 된다.



#### 그럼 이것이 feature map size들의 크기가 다양해도 되는 것과 무슨 연관성이 있니?

![image-20220425214407873](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425214407873.png)



- ##### SPM으로 서로 다른 크기의 Feature map을 균일한 크기의 Vector로 표현이 가능하다.

  - SPM에서 level 1 같으경우 ==> 3개의 값이 나오기 때문에 ==> 3x1로 표현 가능

  - level2 = 3x4 =12

  - level3 = 3x16 = 48

  - 즉 3 + 12 + 48 = 63개 원소의 vector 값으로 표현이 가능하다

    

- ##### 이게 가능한 이유??

  - 그냥 분면으로만 나누면 되기 때문이다
    - 그리고 특징만 뽑아오면 되기 때문
  - 즉 크기가 제각각이여도 그냥 똑같은 수의 분면으로 나눠주면 되기 때문에 상관이 없다



- ##### 이 분면을 나누는 것이 Pooling과 유사하다

  - Pooling을 보면 지정된 사각형에서 필요한 값만 뽑아온다
  - SPM도 분면을 나눠서 필요한 값(특징)만 뽑아옴



### SPP

- pooling

![image-20220425215036920](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425215036920.png)

==> Feature map의 크기와 상관없이 특징들을 뽑아낼 수 있다



### SPP-Net - Image classification

![image-20220425215436780](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425215436780.png)

- 서로 다른 feature map 사이즈 ==> spatial pyramid pooling layer에 넣어준다.

- 분면을 나눔 ex_(4x4, 2x2, 1x1) ==> max pooling

- 16x256-d 

  - 채널의 개수가 256 : 즉 차원이 256개 있다는 뜻 : 즉 두께가 256이라는 뜻

- ##### 이렇게 되면 flatten을 했을때 총길이가 항상 고정된 사이즈로 나오게 된다

- ##### 그래서 fully-connected layers에 넣어줄때 항상 고정된 크기로 집어 넣어줄 수 있게 된다.

- 손실이 일어나지 않을까??

  - 약간의 손실이 일어날 수 있으나 이미지크기  자체에 손을 대는 것 보다는 괜찮은 결과를 내었다



### SPP-Net - object detection



![image-20220425221112091](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425221112091.png)

![image-20220425221126744](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425221126744.png)

- 즉! Selective search에서 뽑아온 데이터의 크기가 제각각 이라도!!
  fixed-length representation의 사이즈는 변하지 않음

- 따라서 FC layer에 똑같은 고정된 사이즈로 Flatten된 값을 넣어줄 수 있게 된다. ==> Dense
- 이미지를 2000개를 넣을 필요가 없음
  - 이유?
  - 하나의 이미지를 넣고 특징을 뽑아냄( 학습 )
  - 있음직한 정보의 애들은 따로 이미지 학습시킨 것(Feature Map)에 넣는 것





### SPP-Net을 RCNN에 적용

![image-20220425221745674](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425221745674.png)

![image-20220425222416191](04_SPP(Spatial Pyramid Pooling)_Net.assets/image-20220425222416191.png)

- 성능 => RCNN과 비교했을때 speed가 굉장히 향상되었다











