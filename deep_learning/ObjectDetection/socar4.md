# socar4

## Backward pass

##### 용어

Entropy

- 엔트로피는 `불확실성의 척도`입니다. 정보이론에서의 엔트로피는 `불확실성`을 나타내며, 엔트로피가 높다는 것은 정보가 많고, 확률이 낮다는 것을 의미합니다.

불확실성이라는 것은 **어떤 데이터가 나올지 예측하기 어려운 경우**라고 받아들이는 것이 더 직관적입니다. 예시를 통해 보는 것이 가장 좋습니다.



- 동전을 던졌을때 ==> 확률1/2

$$
H(x)= -\left( \frac{1}{2} log{\frac{1}{2}} + \frac{1}{2} log{\frac{1}{2}} \right)
$$



- 주사위를 던졌을때 ==> 확률1/6

$$
H(x)= - \left( \frac{1}{6} log{\frac{1}{6}} + \frac{1}{6} log{\frac{1}{6}} + \frac{1}{6} log{\frac{1}{6}} + \frac{1}{6} log{\frac{1}{6}} + \frac{1}{6} log{\frac{1}{6}} + \frac{1}{6} log{\frac{1}{6}} \right)
$$

동전의 엔트로피 값은 약 0.693, 주사위의 엔트로피 값은 1.79 정도로 **주사위의 엔트로피 값이 더 높다**는 것을 알 수 있습니다. 즉, 무엇이 나올지 알기 어려운 주사위의 경우가 엔트로피가 더 높은 것이죠.
$$
H(x)=−\sum_{i=1}^{n} p(x_i) log{p(x_i)}
$$

$$
H(x)=\sum_{i=1}^{n} p(x_i) \left( -log{p(x_i)} \right)
$$

- x값이 커지게 되면 -log값은 기하급수적으로 커짐
- 이때 x가 작아진것보다 log x 가 커지는 것이 훨씬 크기 때문에 전체값은 증가하게 된다.



##### 공꺼내기

다른 예시를 통해서 이해를 좀 더 돕겠습니다.

- 전체 공이 100개이다. 공 하나만 빨간색이고, 나머지는 모두 검은색이다.
- 전체 공이 100개이다. 공 50개는 빨간색이고, 나머지는 모두 검은색이다.

위의 경우에는 직관적으로 **첫 번째 사례에서 검은 색이 나올 확률이 높으니 불확실성이 적겠군** 이라고 생각할 수 있습니다. 실제로 엔트로피를 계산하면 후자가 훨씬 크게 나옵니다.





cross entropy
$$
H_p (q)=−\sum_{i=1}^{n} q(x_i) log  {p(x_i)}
$$

- 실제 q값을 모르는 상태에서 p값을 구하는 것 ==> cross entropy
- 따라서 p를 통하여 q값을 예측하는 것









### Back Propagation

- loss function을 통해서 해당 MLP가 얼마나 작동하고 있는지를 표현

  

Partial Derivative



- 편미분은 함수의 변화량을 얘기할 때 어느 방향 변화량인지 이야기를 해주어야 한다.
- 1변수 함수일경우 ==> 그냥 그 변수의 증감
- 다변수일때는 x1 은 증가하는 방향 x2는 감소방향 x3 그대로? 그럼 이런 표현을 다 해주어야 한다.



chain rule

![image-20220522161126250](socar4.assets/image-20220522161126250.png)

- u의 모든 성분(u1,u2, ...... )으로 거쳐갈 수 있음
- 따라서 모든 성분이 받은 영향을 다 더해줘야함 ==> 다 더해줘야함 ==> 위에 식같이 됨





#### Common Variable

![image-20220522165326669](socar4.assets/image-20220522165326669.png)



#### pytorch에서 tensor 값

- forward를 진행할 때 backward에서 미분값을 위해서 값을 저장을 시켜줘야한다..
- 이떄 pytorch에서 tensor로 바꾸면 forward를 진행할 때 값을 저장시켜주기때문에 가능
- 따라서 np.array를 사용하지 않고 tensor를 사용하게 되는 것이다.



#### Last layer의 Backward pass

##### softmax나오는 식

![image-20220522184051876](socar4.assets/image-20220522184051876.png)

- 두번째
  - 모든 loss값을 더한다
- 세번째
  -  cross entropy 식
- 네번쨰
  - softmax는 원핫 인코딩을 마지막에 사용하기 떄문에
  - 하나의 값 뺴고는 나머지는 다 0값으로 나오게 된다.
  - 따라서 하나의 값만 나오고 앞에 실제 값도 1값이기 때문에 이런 식이 나오게 됨
- 다섯번쨰
  - 이것일 확률/ 전체 확률



![image-20220522184941316](socar4.assets/image-20220522184941316.png)

- 첫번째 항
  - 실제로 





### Optimizer

일반적인 ML

- closed form solution
  - 데이터와 함수, 데이터와 objective(목적) ==> 최적화하는 solution을 바로 구할 수 있는 경우가 많음

DL

- iterative한 방법을 통해서 solution을 구하게 된다.
  - 파라미터의 개수도 너무 많고 이것을 한번에 처리할 수 있는 방법이 없기 때문에
  - 대표적인 예) gradient descent
  - 차원이 3차원정도가 아닌 굉장히 깊은 차원을 다루게 된다
  - 이때 하나의 값이 다른 파라미터에 어떤 영향(하나하나)을 끼치는지는 알수 없음



Parameter space in Deep Learning

- 실제 deep learning 모델의 parameter space는 차원이 굉장히 큼
- globa optimal point를 찾는 것은 불가능
- 따라서 단지 saddle points을 피하고 loca minimal를 찾는데 목표를 함
  - saddle point가 굉장히 많음 (말 안장처럼 생긴 3차원 그래프 모양)
  - 한쪽으로는 감소하고 한쪽으로는 증가하기 때문에 피해야함
- 일반적으로 loca minima들은 비슷한 함수 값을 가짐





#### Stochasitic Gradient Descent SGD

![image-20220523213027062](socar4.assets/image-20220523213027062.png)

- 본인지점에 가장 빠른 감소방향만 찾음
- 거기에 lr을 곱함

- 따라서 한번에 가운데로 가는 것이 아니라 왔다갔다 하면서 가게 된다.
  



#### Momentum

- gradient가 빠르게 변하는 것을 막으면서 update유도 ( 방향을 확확바꾸지 않는다 ) 

![image-20220523213250916](socar4.assets/image-20220523213250916.png)



#### AdaGrad

각각의 parameter별로 optimizer가 파라미터를 얼만큼 업데이트를 기억해주는 것

- 전에 많이 업데이트를 해주었다면 다음에는 업데이트를 덜 해주게 된다.
- 위에 알고리즘 같은 경우는 lr값이 일정한 반면 Ada같은 경우에는 그렇지 않는 것이 특징이다.























