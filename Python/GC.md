# Garbage Collector

> - 출처
>   - https://medium.com/dmsfordsm/garbage-collection-in-python-777916fd3189

**기존 메모리관리의 문제점**

- 필요없는 메모리를 비우지 않을때 => 메모리 누수가 발생
- 사용중인 메모리 비우기 => 존재하지 않는 메모리에 접근하려고 하면 프로그램이 중단되거나 메모리 데이터 값이 손상될 수 있음



### Python의 GC 구현

- Reference counting
- Generational garbage collection



### CPython의 Reference Counting

- Python에서 객체를 만들 때 마다 기본 C객체에서는 **Python유형(list, dic, func)과 reference count가 생성** 된다.
- **객체가 참조될 때마다 count를 세는 것**
  - 즉 reference counting이 0이 되면 메모리 할당이 해제된다.



### Python의 Reference Counting

- 변수에 객체 할당
- data structure에 객체 추가 (list, class에 속성추가하는 등)
- 객체를 함수의 인수로 전달

```python
import sys
a = 'hello'
sys.getrefcount(a) => 2

b = [a]
sys.getrefcount(a) => 3

c = {'first': a}
sys.getrefcount(a) => 4
```



### Generational Garbage Collection

> - generation
> - threshold

- 객체가 순환 참조하면 어떻게 작동할까?

```python
a = []
a.append(a)
del a
```

- 참조 횟수는 1이지만 이 객체는 더이상 접근할 수 없다.
- reference counting방식으로 메모리에서 해제될 수 없음



**generate란? **

- 새로운 객체 = 1세대
- 가비지 수집 프로세스를 실행하고 객체가 살아남으면 => += 1세대
-  Python 가비지 수집기는 총 3세대



**threshold란?**

- 각 세대마다 가비지 컬렉터 모듈 => 임계값 개수의 객체가 존재
- 임계값 초과 => 가비지 콜렉션이 콜렛견 프로세스를 trigger한다.



특징

- reference counting과 달리 동작을 변경할 수 있음
  - 임계값 변경
  - garbage collection process를 수동으로 trigger
  - garbage collection process를 모두 비활성화



### GC가 성능에 영향을 끼치는 이유

- 조건 : garbage collection을 수행하려면 응용프로그램을 완전히 중지해야함
- garbage collection 
  - 주기가 짧음 => 응용프로그램이 중지되는 상황 증가
  - 주기가 길음 => 메모리 공간에 가비지가 많이 쌓임



### Manual Garbage Collection (수동)

- Time Base

  - 고정된 시간마다 GC호출

    

- Event Base

  - 이벤트 발생시 GC호출
  - ex) 사용자가 응용 프로그램을 종료하거나 응용프로그램이 중단 상태일때 호출



### 결론

- GC 동작을 수정하지 말자
  - 이유 : 
    - Python의 장점 => 생산성이 높다는 것
    - 차라리 컴퓨터 자원을 증가시키는 것이 좋음
