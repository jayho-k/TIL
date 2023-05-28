# Mulit_Processing

다중 프로세서를 최대한 활용할 수 있게 하는 함수

[Python multiprocessing.Pool 멀티프로세싱 2](https://tempdev.tistory.com/27?category=845382)

![](Mulit_Processing.assets/2022-11-24-10-00-56-image.png)

#### 생성

처음 **Pool**을 생성할 때에 사용될 프로세스 수를 지정할 수 있다. 만약, 주어지지 않는다면 **os.cpu_count()** 의 값으로 지정된다.



##### with문과의 사용

**with**문과 **Pool**을 함께 사용할 수 있다. **__enter__** 엔 **Pool**의 생성이,  **__exit__** 엔 **terminate()** 가 호출된다.

```python
from multiprocessing import Pool

if __name__ == '__main__':
    with Pool(4) as p:
        # do something here with Pool
        # blabla
        # blablabla
```



#### 종료하기

##### join()

- Pool의 모든 프로세스들의 종료가 완료되기를 기다린다.



##### close()

- 더 이상 Pool에 추가 작업이 들어가지 않는다는 것을 알려줌



##### terminate()

- 현재 진행 중인 작업이 있더라도 즉시 pool 종료



#### 실행

#### apply()

- Pool 에게 작업하나를 시킨다
  
  - 그 작업이 완료되지 않으면 메인 프로세스에서 다음 줄의 코드를 실행하지 않는다

- **apply_async**는 **apply_async**을 사용한 줄에서 작업이 다 끝나지 않아도 메인 프로세스의 다음 줄을 실행할 수 있다.



##### apply_async

- Pool에게 작업 하나를 시키고, AsyncResult를 반환
  
  - AsyncResult에서 get()을 호출하면 작업의 반환 값을 얻을 수 있다.
  
  - 하지만 get을 호출하면 그 작업이 끝나기 전까지 메인 프로세스에서도 다음줄로 넘어갈 수 없다



##### map, map_async()

- iterable에 대해 동일한 함수를 멀티 프로세싱을 이용하여 처리할때 사용
  
  - 함수는 단일 인자를 받아야한다.

- imap, imap_async() : 반환값이 iterator이다



##### starmap(), starmap_async()

- map과 같지만 두개 이상의 인자를 받을 수 있음




























