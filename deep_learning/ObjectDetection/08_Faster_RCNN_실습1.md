# 08_Faster_RCNN_실습1

##### 패키지를 고를 때 유의할 점

- backbone을 어떤것을 사용해서 object detection을 구현했는지
- 논문 또는 kaggle등 어떤것을 어떤 조합으로 주로 사용하는지를 확인하고 패키지를 고르는 것이 중요하다.



## MMDetection

- config 기반
- Pytorch 기반



#### 구성요소

![image-20220502130311970](08_Faster_RCNN_실습1.assets/image-20220502130311970.png)



#### MMDetection Training Pipeline

![image-20220502130858493](08_Faster_RCNN_실습1.assets/image-20220502130858493.png)

- loop가 돌기 시작하면 중간에 멈출수 없음
- 따라서 callback함수 또는 hook을 걸게 된다. ==> 예를 들어 학습도중 성능이 더이상 나오지 않을 경우 등등















