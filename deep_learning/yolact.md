yolact

[(논문리뷰&amp;재구현) YOLACT 설명 및 정리 - (1) :: 프라이데이](https://ganghee-lee.tistory.com/42)

trainlation invariance

CNN에서 translation invariance란 input 위치가 달라져도 output이 동일한 값을 갖는 것을 뜻함



![](yolact.assets/2022-09-04-18-56-30-image.png)

1. backbone을 통해서 feature map을 먼저 뽑아낸다 - resnet사용

2. FPN

3. 두가지 경로로 나뉨
   
   - Prediction Head
     
     - 
   
   - Protonet
     
     - Backbone에서 생성한 5개의 feature map 중에서 가장 deep한 P3 feature map을 사용하게 된다.
     
     - 이유
       
       - 깊은 featuer map일수록 이전 해상도들에서의 feature 정보를 모두 포함하므로 robust한 mask를 생성할 수 있다.
       
       - 고 해상도 feature map일수록 작은 object에 대해 좋은 성능을 보인다.

4. 두개의 병렬 subtask가 마지막에 합쳐짐 => final mask를 생성하게 된다.






























