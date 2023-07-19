# 1x1Conv

특징

- Feature map의 채널 수를 감소 시킴
- 비선형성 증대
- 연산량과 파라미터 수 감소 가능

- 1x1x32Conv => 6x6x32 feature map 이 만들어짐

- 거기서 3x3x64Conv => 6x6x64가 만들어지게 된다

  - 보통 1x1하나로 하지 않고 3x3을 추가하여 만들게 된다.  

  - 이렇게 하면 Conv작업을 2번하게됨

  - 이때 비선형성이 증가하게 된다.

    

1x1 Convolution을 통한 Feature Map 채널 깊이 압 축

![image-20220616165935369](1x1Conv.assets/image-20220616165935369.png)



1x1 conv를 적용할 때 vs 안할 때























