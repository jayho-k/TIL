# 01_Celery

1. 동작원리 파악
   - 다른 대안은 없는지 확인
2. tutorial로 코드 생성
3. 현업에서 사용하는 사례 분석
4. 현재 나의 상태에서 어떻게 사용하는 것이 좋은지 테스트



## Getting Started



## Celery - Calling API

> - apply_async()
> - delay
> - calling(\__call__)

**apply_async()**

- Sends a task message
- 메시지를 보내는 방법
- return : AsuncResult

**delay()**

- Shortcut to send a task message
- execution option을 지원하지 않음
- return : AsuncResult

**calling**

- worker를 통해서 execution하는 것이 아니라 현재 process가 맡아서 진행하는 것
- return : return 값

```python 
from proj.tasks import add
add.apply_async((2,2)) # return : AsyncResult >> 인자를 tuple로 넘겨줘야 함
add.apply_async((2,2), queue='queue name', countdown) # 여러 옵션이 가능
add.delay(2,2) # return : AsyncResult
add(2,2) # return : 4
```

```python
res = add.delay(2,2)
res.get(timeout=1) # 4 / 기다리는 시간이 1초넘으면 timeout으로 간주
res.id # id 값 return
res.failed() # True
res.successful() # True
res.state # 'FAILURE'
```



## Celery Standalone

```yaml
celery-standalone:
  build:
    contenxt: standalone_celer
  volumes:
    - ./standalone_celery:/app
  command: celery --app=main worker -l INFO
  depends_on:
    - redis
```

**Entry Point**

```python
from celery import Celery

# 1번째 방법
app = Celery(
	'worker',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include=['worker.tasks'], # .py 파일들 등록
)

# 2번째 방법
app = Celery(
	'worker',
    include=['worker.tasks'],
)
app.config_from_object('celeryconifg') # 

if __nam__ == '__main__':
    app.start()
```



## Celery - Tasks Routing

https://docs.celeryq.dev/en/stable/userguide/routing.html

- Queue를 지정해서 Task를 처리할 수 있음
- 장점
  - Load Balancing
  - Resource Allocation
  - Priority Handling
    - 어떤 Task를 먼저 실행하는지 지정할 수 있음
  - Isolation

**1. command를 통해 Queue 정의 (Consumer)**

- celery를 queue1로 정의. queue1은 celery가 work을 처리하게 된다.
- celery-standalone을 queue2 로 정의.  queue2로 온 work은 celery-standalone 처리

```yaml
celery:
  build:
    contenxt: standalone_celer
  volumes:
    - ./standalone_celery:/app
  command: celery --app=main worker -l INFO -Q queue1 # queue1
  depends_on:
    - redis

celery-standalone:
  build:
    contenxt: standalone_celer
  volumes:
    - ./standalone_celery:/app
  command: celery --app=main worker -l INFO -Q queue2 # queue2
  depends_on:
    - redis
```

**2. config를 통해 정의 (publisher)**

- 각각의 function 또는 package를 어디로 보낼지를 정의하는 것
- 따라서 worker.task.dumb를 진행하게 되면 queue1로 보내게 된다.

```python
# 1 / 
app.conf.update(
	task_routes = {
        'worker.task.dumb':{ # regular expression 사용 가능. ex) 'worker.task.*'
            'queue':'queue1'
        },
        'worker.task.add':{
            'queue':'queue2'
        },
    }
)

# 2
app.conf.task_routes = {
    'worker.task.dumb':{
        'queue':'queue1'
    },
    'worker.task.add':{
        'queue':'queue2'
    },
}
```



## Celery - Priority Queue

- https://docs.celeryq.dev/en/v5.5.3/userguide/routing.html

```python
# redis
app.conf.broker_transport_options = {
    'priority_steps': list(range(10)),
    'sep': ':',
    'queue_order_strategy': 'priority',
}

['celery', 'celery:1', 'celery:2', 'celery:3', 'celery:4', 'celery:5', 'celery:6', 'celery:7', 'celery:8', 'celery:9']

# Rabbit MQ
from kombu import Exchange, Queue

app.conf.task_queues = [
    Queue('tasks', Exchange('tasks'), routing_key='tasks',
          queue_arguments={'x-max-priority': 10}),
]
app.conf.task_queue_max_priority = 10
app.conf.task_default_priority = 5

from kombu import Exchange, Queue
app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('videos',  Exchange('media'),   routing_key='media.video'),
    Queue('images',  Exchange('media'),   routing_key='media.image'),
)
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'default'

```

### Exchange types

익스체인지 타입은 메시지가 익스체인지를 통해 어떻게 라우팅되는지를 정의한다.

표준으로 정의된 익스체인지 타입에는 다음이 있다:

- `direct`
- `topic`
- `fanout`
- `headers`

또한 RabbitMQ 플러그인을 통해 제공되는 비표준 익스체인지 타입도 존재한다.
 예를 들어 Michael Bridgen이 만든 **last-value-cache 플러그인** 등이 있다.



### Direct exchanges

Direct 익스체인지는 **정확히 일치하는 라우팅 키**로 메시지를 매칭한다.
 예를 들어 `video` 라는 라우팅 키로 바인딩된 큐는
 라우팅 키가 정확히 `video` 인 메시지만 수신한다.

### Topic exchanges

Topic 익스체인지는 **점(`.`)으로 구분된 단어들**로 이루어진 라우팅 키를 사용하며,
 다음과 같은 와일드카드 문자를 지원한다:

- `*` : 단어 하나와 매칭
- `#` : 0개 이상의 단어와 매칭

예를 들어 다음과 같은 라우팅 키들이 있다고 하자:

- `usa.news`
- `usa.weather`
- `norway.news`
- `norway.weather`

이 경우 가능한 바인딩은 다음과 같다:

- `*.news` → 모든 뉴스
- `usa.#` → 미국(usa)에 속한 모든 항목
- `usa.weather` → 미국의 날씨 정보만



## Celery - Task Grouping

- Task들을 한번에 Grouping해서 병렬로 Execute하는 방식

**Primitives**

- Group : 병렬로 순서 없이 실행되는 것을 의미
- Chain : 여러개의 task를 linking해서 순차적으로 실행
- Chord 
- Starmap 

**Signature** : task를 추상화하는 것

```python
# Group
from celery import group, signature
from worker.tasks import add, xsum

job = group(signature('worker.tasks.add', args=(i, i)) for i in range(10))
result = job.apply_async()

job = group(add.s(i, i) for i in range(10))
result = job.apply_async()
"""
<GroupResult: 10c0dfa3-489b-4a86-a101-90ac77b2e64f [e500072b-214d-48a4-adc6-f212d5859a11, 10622db4-b849-464e-a067-8e2e0f83d849, 762a60e6-d2c5-42f0-b150-a5868834e0bf, cefc7e86-6ba1-42d1-8471-a4728c9eb304, 8d0221ff-432e-4498-bcd5-7c7ce7825b02, 1e4f76bb-22fa-4a3a-ba9c-ec8b0cc205c7, 3db0dcd9-3807-45a2-80fe-cdaa1101feaf, be94d86e-2a6f-4596-b068-8f2c6b3895f7, ba61b0c9-c434-427a-8d06-8e18529b94e9, 631c3ce0-7c92-4c53-af31-ff38ea78ce0f]>
"""
result.get()
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


# Chain
from celery import chain

workflow = chain(add.s(2, 2), add.s(4), add.s(8))
result = workflow.apply_async()
result.get()
# 16


# Chord
from celery import chord

callback = xsum.s()
header = [add.s(i, i) for i in range(10)]
result = chord(header)(callback)
result.get()
# 90


# Starmap
result = add.starmap(zip(range(10), range(10))).apply_async()
result.get()
[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```



## Celery - Task Rate Limit

- 최대 Tasks를 지정해서 초당, worker당 얼마나 실행시킬지를 정해주는 것
- Rate Limit Format : number / time_unit ('s': 초, 'm': 분)
  - 만약 10/m 으로 rate limit을 잡고, 2개의 worker가 있다면 각각의 woker들은 1분당 10개의 tasks를 실행하기 때문에 총 1분당 20개의 task가 실행된다.
- **use case**
  - Rate Limits를 가진 external APIs 를 사용하게 될 때
  - DB, other service에 high loads가 발생하는 task들

```python
# 방법 1
app.conf.task_default_rate_limit = '5/m'

# 방법 2
@shared_task(queue='celery', rate_limite='1/m')
def add(x, y):
    return x + y

```



## Synchronous, Asynchronous Task

```python
@shared_task(queue='celery')
def sleep_task():
    time.sleep(10)
    return 

def sync_task():
    result = sleep_task.apply_async()
    print("Waiting...")
    res = result.get() # process가 계속 기다리게 되는 현상 발생

def async_task():
    result = sleep_task.apply_async()
    print("Not Waiting...") # process가 기다리지 않게 된다.
    print(result.id)
    
```



## Signal 

https://docs.celeryq.dev/en/v5.5.3/userguide/signals.html

- Signal은 Task의 액션을 기준으로 전, 후 등에 어떤 동작을 할지를 정의하는 것

```python
from celery.signals import task_prerun, task_postrun, task_failure

# Define signal handlers
@task_prerun.connect(sender=add)
def task_prerun_handler(sender, task_id, task, args, kwargs, **kwargs_extra):
    print(f"Task {task_id} is about to run: {task.name} with args {args}")

@task_postrun.connect(sender=add)
def task_postrun_handler(sender, task_id, task, args, kwargs, retval, state, **kwargs_extra):
    print(f"Task {task_id} has completed: {task.name} with result {retval}")

@task_failure.connect(sender=add)
def task_failure_handler(sender, task_id, exception, args, kwargs, traceback, einfo, **kwargs_extra):
    print(f"Task {task_id} has failed: {sender.name} with exception {exception}")
    task_failure_clean_up.delay(task_id=task_id) # type: ignore

@shared_task(queue='celery')
def task_failure_clean_up(task_id, *args, **kwargs):
    print(f"Task {task_id} clean up process has been started")

# simulating task signal
def simulating_task_signal():
    # Call the Celery task asynchronously
    result = add.delay(2, "error") # type: ignore

    # Get the result of the task
    final_result = result.get()
    print("Final Result:", final_result)


```
