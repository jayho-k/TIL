# Terms for DL

### fine tuning

언제 사용함?

- 승용차를 인식하는데 학습되어 있는 것들을 트럭을 인식할때 등등에서 사용한다.
- 더 많은 시간들을 save 할 수 있다.

어떻게 사용함?

1. 비슷한 모델 importing하기2
   
2. out layer 제거하기 (이전 모델에 대하여 굉장히 specific 하기 때문에)
   (전모델 : 차인지 아닌지// 이번모델: 트럭인지 아닌지가 궁금 그래서 삭제)
3. 선택
   모델 추가 or 제거 해줘야할 수도 있음
   필요한 데이터에 따라서 추가 삭제 해줘야할 때 
   ===> freezing layer 을 해줘야함 ==> layer얼려서 수정 안하게 함
   weights를 새로운 모델을 새로운 데이터로 트레이닝 할때 update하지 않음
4. 새로운 데이터로 모델을 training하는 것

- 인풋 레이어들은 수정할 필요가 있음 ==> 새로운 데이터로 트레이닝
- weights는 가만히 냅둠



### network?

- 디바이스를 서로 연결시켜주는 것
- 컴퓨터 네트워크: 정보와 하드웨어 데이터 소프트웨어 등을 서로 공유, 의사소통하게끔 연결하는 그룹



### superpixel?

- 비슷한 벨류들 끼리 그룹화를 시킴으로써 복잡도를 줄이는 것
- 이유: 분석을 더욱 간단하게 하기 위해서



### downstream in networking

- 네트워크 서비스 제공자에서 고객에서 보내는 데이터를 의미한다
- 예를 들어 다운로드와 같은 것을 의미한다



### fully convolutional network(FCN)



### enumerate

- 열거하다



### scale of an image?

- 이미지를 resizing하는 것
- When scaling a raster graphics image, a new image with a higher or lower number of pixels must be generated. In the case of decreasing the pixel number (scaling down) this usually results in a visible quality loss.
- 픽셀수를 낮출 경우에는 퀄리티가 안좋아진다



###  raster:

- 컴퓨터에서 화상 정보를 표현하는 한 가지 방법. 
- 이미지를 2차원 배열 형태의 픽셀로 구성하고, 이 점들의 모습을 조합, 일정한 간격의 픽셀들로 하나의 화상 정보를 표현하는 것이다.
- 즉 한 줄에서 연속된 픽셀들의 집합을 래스터라고 한다



### CNN

- 구성:
  - conv layer => pooling => conv layer2 => pooling 을 겹겹히 쌓는 구조이다.
  - conv layer :  (필수)
    - 입력데이터에 필터를 적용
    - 활성화 함수를 적용
  - pooling: (선택)
  - Fully Connected layer:
    - cnn 마지막부분에 이미지 분류를 위한 Fully Connected레이어가 추가
  - Flatten layer
    - 이미지의 특징을 추출하는 부분과 이미지를 분류하는 부분사이(classification)에 이미지형태의 데이터를 배열 형태로 만드는 레이어가 추가

#### 1.1 합성곱, Convolution

![image-20220130173007974](Terms for DL.assets/image-20220130173007974.png)

이렇게 추출해 오는 것을 합성곱이라고 한다.

이렇게 추출해 온 결과 = Feature map이라고 불린다.



#### 1.2 필터(Filter) = Kernel & Stride

- 커널 사이즈르 정해서 feature map을 만들게 된다
- stride는 몇칸씩 이동하는지를 말하게 된다.

![image-20220130173428346](Terms for DL.assets/image-20220130173428346.png)

- 채널이 여러개인 경우
  - 각 채널을 순회하면서 conv를 계산하게 된다. ==> feature map을 만듬
  - 각채널의 conv map을 합산 ==> 1개의 feature map을 만들게 된다.
- Activation map
  -  Feature map행렬에 활성함수를 적용한 결과이다. 
  - layer의 최종 출력 결과는 Activation map이다.



#### 1.3 Pooling layer

![image-20220130174243369](Terms for DL.assets/image-20220130174243369.png)

- Actvation map이 나온 뒤에 pooling을 진행하게 된다.
- Pooling 레이어를 통과하면 행렬의 크기 감소
- Pooling 레이어를 통해서 채널 수 변경 없음













