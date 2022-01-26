# Faster R-CNN(region based CNN)

Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks

- RPN을 이용 = 물체가 있을 것 같은 것을 찾음, GPU를 이용 
- detection network???
- CPU에 넣는 것과 GPU에 넣는 것에 차이가 무엇??
- fine-tuning: 작은 조정 (전에 사용한 weight 사용, )

### 초록:

- RPN와 detection network가 함께 convolutional features를 공유하고 있기 때문에 region proposal 에 필요한 연산을 사실상 거의 없는 형태로 만들었음

​		==> RPN에 필요한 시간을 획기적으로 줄임

- RPN은 물체가 위치에 있는지 없는지만 판단, (고양이인지 개인지 판단하지는 않음)
- end to end
- RPN과 Fast R-CNN을 하나의 single 네트워크로 합칠 수 있도록 함
  - 이때 둘다 convolutional network의 형태이기 떄문에 이미지의 특징을 추출하는 과정이 공유될 수 있다. (앞에서 convolutional layer를 두어서 같이 공유하게 만듦) ==> 시간을 단축

- 네트워크가 어디를 봐야한다는 것을 제시해주기 떄문에 성능이 향상 되었음
- 5fs = 초당 5장의 이미지를 처리할 수 있다. (real time) 가능
- 



### 1. introduction

- 그래서 Region proposal을 GPU로 올리게 되었음
- 하지만 이때 어떻게 sharing computation(같이 계산)이 가능할 것인가에 대한 논의가 필요
- 따라서 알고리즘을 변경함 ==> 사실상 공짜로 이용

- 앞쪽에 몇 가지 layer들만 추가해주면 되기 때문이다

- RPN은 다양한 크기와 박스비율을 예측할 수 있음(다양한 박스 형태)
- 다양한 anchor 박스를 사용함으로써 예측 ==> 본 논문 9개를 사용
- RPN과 Fast RCNN을 통합하기 위해서 region proposal(물체가 어디 있는지) 과 object detection(종류와 위치)을 번갈아 가면서 fine tuning(?)을 진행하게 된다. == > 적절히 공유 될 수 있고 빠름



### 2. related work

### 3. faster RCNN

![image-20220123174814835](C:\Users\장호\AppData\Roaming\Typora\typora-user-images\image-20220123174814835.png)

1.  이미지가 주어짐
2. conv layer를 거침 ==> feature map을 뽑아냄
3. 이런한 feature map이 공유가 된다. == RPN과 classirier에 둘다 들어가게 된다.
4. RPN: 물체의 존재 여부를 판단 , 만약있다면 정확히 어디에 위치하고 있는지 말해줌

5. 각각의 위치하는 물체의 종류를 classifier에서 판단하게 된다.

​	==> RPN은 classifier에게 이런 곳을 더 중점적으로 확이해봐라고 알려주게 되는 것



#### 3.1 Region Proposal Networks

- (zeiler and ergus model )ZF(2013년도 논문 VGG 이전에 많이 사용했었음) 또는 (Simonyan and Zisserman model) VGG와같은 CNN 아키텍쳐를 사용하게 된다.

1. feature map을 n x n 크기의 윈도우를 슬라이딩하는 방식으로 prediction을 진행하게 된다.

2. 각각의 sliding window는 더 작은 차원 feature로 mapping을 진행하게 된다.
3. 이때 이 feature들은 2가지(box regression layer와 box classification layer)로 넣게 된다. (?)

![image-20220123175741665](C:\Users\장호\AppData\Roaming\Typora\typora-user-images\image-20220123175741665.png)

1. 한장의 이미지를 conv 에 넣어서 ==> conv feature을 뽑음
2. 다양한 크기의 anchor box를 이용하여 쭉 슬라이딩을 하게 된다. 
3.  256 차원으로 mapping을 먼저 함 
4. cls, reg에 넣게 된다. 

   (총 9개의 anchor박스를 사용함, 1x1 2x1 1x2 등등을  사용함)

##### 3.1.1anchors

- 각각의 슬라이딩 로케이션에서 동시에 region proposals 을 예측하게 된다 이땐 최대 가능한 proposals을  예측 ==> 즉 각각의 위치마다 총 k개의 박스를 사용하게 된다.
  가능한 k개의 proposal을 이용하여 예측을 진행한다.
- reg => 4k(x,y, 너비, 높이)개의 아웃풋을 가지고 있고
   이것이 k개의 박스로 편성하여 인코딩하게 된다.
- cls는 2k의 스코어로 ouput을 내고 이때 가능성 여부를 판단하게 된다
  ex)  물체가 있음 72% // 없음  28% // 이런식으로 각 사진당 2가지의 ouput을 내도록 해준다.
- 3가지 scales, 3가지 종류의 비율 ==> 총 k = 9의 앵커 박스를 사용하게 된다.
  ex) feature map of size = W x H  ==> WHk개의 anchor가 사용될 것이다.

#####    Translation Invariant Anchors( object detection에서 중요함)

- translation invariant: 이미지에 대하여 이동이 가해진다고 하더라도 traslation invariant가 보장이 되기 때문에 좋은 특성을 가지고 있다.
  슬라이딩 기법을 이용하는 것이기 때문에 이미지에 변형이 일어난다 하더라도 invariant한 장점을 가지고 있다. 



- multi scale anchors 
  - 전통적인 image/feature pyramids 방식 (이미지의 크기를 변형하면서 각각의 크기의 feature map을 계산 해야함 ==> 시간이 오래걸리게 된다.)



- sliding winow 방식



- anchor의 피라미드 형태 (sliding window에서 anchor를 추가한 방식)

  - image/ feature map을 한번만 conv에 넣고 다양한 anchor를 이용해서 처리함

  - regression으로 더 정확한 위치를 찾게 된다.

#### 3.1.2 Loss Function

- RPN를 Training하기 위해서  각각의 anchor에 대해서 Binary class label을 진행하게 된다
  (즉 거기에 물체가 존재하는지 안하는지를 판단한다. )
- positiv lable을 주는 경우 = 2가지  ==> 정답이라고 판단
  - IoU를 사용  (교 / 합집합) 두가지 바운딩 박스가 얼마나 겹쳐있는지에 대한 척도
    IoU = 1 ==> 정확히 두개의 박스가 동일하다는 것을 의미한다. 
  - 1. 엥커들 중에서 IoU값이 가장 높을 경우 : 정답이라고 판다
    2.  IoU가 0.7 이상일 경우 : 정답이라고 판다  

- 유의할 점

  - 한 물체에 여러가지 anchor 박스의 IoU의 값이 0.7이상인 경우가 있을 수 있음
    즉 여러개 박스가 한물체에 대해서 동시에 정답이라고 외치는 경우가 있을 수 있음
  - positible sample자체가 존재하지 않을 수 있음
    따라서 가장 높은 IoU의 값을 채택할 필요가 있음

  - IoU의 값이 0.3이하일 경우에는 오답이라고 외친다.
  - Positive or Negative 도 아닌 경우에는 object에 영향을 끼치지 않도록 한다.



- loss function (결과적으로 이 공식을 사용하게 된다.)

![image-20220123184611568](C:\Users\장호\AppData\Roaming\Typora\typora-user-images\image-20220123184611568.png)

![image-20220125144703588](Faster R-CNN(region based CNN).assets/image-20220125144703588.png)



x,y ==> 바운딩박스의 중간점 위치

너비와 높이로 바운딩박스의 크기를 설정한다. 



regression을 위한 feature의 크기 = 3 x 3

bounding 박스는 ==> 말그대로 사진에 네모쳐져있는 것들

anchor박스는 ==> 여러가지 크기로 특징을 추출하는데 사용되는 것?

####  Training RPNs

- end to end 방식을 사용하였다
- 모든 엥커에 대해서는 고려하지 않고 랜덤하게 256가지를 골라서 학습하게 된다.
- positive anchor와 negative anchor의 비율이 1: 1정도로 가능하다면 될 수 있도록 한다.(128:128)

- 이 모델에 맞게 hyper parameter정보가 나와있으니 참고 할 것



#### 3.2 Sharing Features for RPN and Fast R-CNN

- fast R-CNN detector와 RPN을 어떻게 공유할 수 있는지에 대하여 나와있음

- detection network = Fast R-CNN에서 가져옴
- \+ RPN

how to share?  3가지

1.  **Alternative training**: 
   - 번갈아가며 학습
   - RPN 학습 >> Fast R CNN학습 >> 다시 RPN 
2. Approximate joint training
   - RPN 과  Fast R CNN을 합병시켜서 하나의 네트워크로 진행한다.
   - 구현하기 쉬움
   - propoal boxes들의 coordinates 의 미분값을 무시하게 된다
   - 따라서 근사치가 나오게 된다.
   - 정확도가 살짝 부족함
3.  Non _ Approximate joint training



**4-step Alternating training**

1. RPN 학습 >> 전체 네트워크에 대해서 학습을 진행한다.
2. RPN에서 추출한 proposal을 이용해서 Fast R CNN학습
   2단계까지는 conv layers가 공유되지 않는다. 
3. RPN단계에서 포함되지 않는 conv layer는 완전히 고정한 상태로 RPN에 포함되어 있는 추가적인 conv에 대해서만 fine tunning을 하게 된다. 
4.  conv layer는 완전히 고정한 상태로 Fast R CNN에서만 포함되어 있는 layer에 대해서만 학습을 진행하게 된다.

==> 4번만 반복해도 충분하다고 말함



- 이미지 바운더리를 크로스하는 anchor boxes들은 조심해서 다룰 필요가 있음
- 이 논문에서는 loss에 영향이 가지 안도록 설정을 했음
- 논문에서 anchor 박스가 20000을 만들었다면 각이미지당 6000개 정도의 anchor박스를 선택적으로 사용하게 된다.

- 클라스가 같은 중복된 박스들을 처내기 위해서 non-maximum suppression(NMS)를 사용하게된다. ==> 굉장히 많이 사용되는 방법 중 하나이다.
- 그리고 NMS를 위한 IoU= 0.7를 사용함 ==> anchor 박스 2000개로 줄음
- 6000개에서 2000개로 줄었다고 해서 NMS가 정확도에 영향을 주진 않았음
- NMS 이후에 top-N 개에 proposal regions만 사용된다.
- 즉 학습을 진행 할 떄 2000개 사용하더라도 실제 evolation을 진행할 때는 유동적으로 갯수를 정하게 된다.



#### 4. Experiments (실험결과)

4.1 pascal voc 2007 과 12년

이 데이터 셋이 많이 사용된다.

conv 을 공유할 때 더 좋은 값



성능은 VGG가 더 높지만 속도는 ZE가 더 가볍기 떄문에 빠르다

anchor box = > 3scale 3ratio ==> 가장 좋은 값이 나왔음



2.4 MS COCO에 대한 실험 결과





















