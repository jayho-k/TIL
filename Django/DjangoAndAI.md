# 장고와 AI

장고란?

- 데이터베이스의 액세스, 세션, 라우팅, 다국어 지원등을 다루는 자체적인 ORM계층이 포함되어 있다

장고의 단점

- 속도
  
  - 앱이 최적화되어서 만들어졌는지를 항상 확인해야한다.
  
  - 내부의 속도를 확인하고 모든 장애물을 찾아낼 수 있는 자체적인 벤치마크 도구를 제공
  
  - 캐싱을 비롯해서 수많은 최적화 도구들도 적용가능
  
  - 속도 문제시 장고 자체에 문자가 아님 => 적절하지 못한 환경설정과 아키택처 설계의 문제일 경우가 많음





장고에서 AI모델을 돌리면 좋은점

- 장고안에 모델을 직접 이식하는 방법을 통해서 굳이 따로 서버를 두지 않아도 된다



문제

- 웹서버에서 모델을 불러 값을 넣은 후 예측값을 받는 과정은 엄청난 시간이 소비가 된다.



모델이 돌아가는 과정

- 모델을 부름

- 값을 넣어줌

- 그것의 예측값을 받음

2,3 번과정은 모델의 구조를 바꿔야 가능한 방법



#### 방법 : 1번 과정의 시간을 줄일 것임

app.py를 참조한다.

- app.py는 여러번 불러오는 상황을 막기에 최적의 환경을 가진다.

- Python 내부의 로직이 복잡하여 오래걸리거나 한번 초기화 해둔 파일을 계속 사용하고 싶은 경우 app.py를 사용하면 될 것 같습니다.

```python
from django.apps import AppConfig
from deep.model import DeepModel 

class ShopConfig(AppConfig):
    name = 'shop'    model = DeepModel()
```





Flask나 Django로 비동기, 멀티스레드/프로세스를 하기위해서

Funicorn,Celery,Nginx등등 해야한다. ==> 이것에 대해서 알아보기

[OpenCV + WebApp (CV Lecture) - YouTube](https://www.youtube.com/playlist?list=PLvX6vpRszMkwECdbxNX8s9R-vcUFGqqtC)



장고에서 모델을 쓰는 방법

1. recommand.py과 같이 파일을 따로 만들어준다

2. view파일에서 recommand.py모델을 불러온다






























