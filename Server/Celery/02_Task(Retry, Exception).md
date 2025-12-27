# 02_Task(Retry, Exception)

- task execution, worker status, operational metrics 등의 real time over view를 확인할 수 있음



### autodiscover_tasks

```python
autodiscover_tasks(pakages=None, related_name='tasks', force=False)
```

- **pakages** : directory의 location
- **related_name** : file name

- 인자를 하나도 넣지 않게 되면 파일 이름이 `tasks.py` 인 파일들만 import를 해오게 된다.
- 따라서 인자를 넣어줘야할듯
  - `app.qutodiscover_tasks(['worker', worker.celery_tasks])`
  - 위와 같이 worker를 먼저 import를 해줘야한다.
- \__init__ 파일이 있어야 import를 인식하게 된다.





## Task ingeritance

```python
from worker.celery import app
from celery import Task

class CustomTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if isinstance(exc, Exception):
            logging.error(f"Error happens on {task_id}")

# Register custom task calss with Celery
app.task(base=CustomTask) 

# CustomTask를 사용하고 싶은 Task에 base로 지정해준다.
@app.task(queue='celery', base=CustomTask)
def task():
    pass
```



## Retry

https://docs.celeryq.dev/en/stable/userguide/tasks.html#retrying

```python
@app.task(bind=True)
def send_twitter_status(self, oauth, tweet):
    try:
        twitter = Twitter(oauth)
        twitter.update_status(tweet)
    except (Twitter.FailWhaleError, Twitter.LoginError) as exc:
        raise self.retry(exc=exc)


@app.task(bind=True, default_retry_delay=30 * 60)  # retry in 30 minutes.
def add(self, x, y):
    try:
        something_raising()
    except Exception as exc:
        # overrides the default delay to retry after 1 minute
        raise self.retry(exc=exc, countdown=60)

# 
class BaseTaskWithRetry(Task):
    autoretry_for = (TypeError,)
    max_retries = 5
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = False


```

```python
# Register custom task class with Celery
app.task(base=CustomTask)

@app.task(queue='celery', base=CustomTask,
          autoretry_for=(IOError,), max_retries=3, default_retry_delay=10)
def my_super_task():
    # try:
    raise IOError("File X does not exists")
    # except IOError as e:
    #     logging.error(e)
```



## Group Result

- 주의
  - 4개 중에 하나만 Error가 나더라도 Fail로 뜨게 된다.

```python
from celery import group
from tasks import add

job = group([
            add.s(2, 2),
            add.s(4, 4),
            add.s(8, 8),
            add.s(16, 16),
            add.s(32, 32),
])

result = job.apply_async()

result.ready()  # have all subtasks completed?
# True
result.successful() # were all subtasks successful?
# True
result.get()
# [4, 8, 16, 32, 64]
```



## Event Driven System

> - 문제가 생겼을 때 어떻게 할 것인가?
> - Consumer에서 문제가 생겼을 때 

### Dead Letter Queue (DLQ)

- Queue인데 전달하지 못한 메시지를 저장하는 용도의 Queue
- Consumer가 성공적으로 work을 수행하지 못하였을 때 사용함
  - Consumer에 의해 reject 된 경우
  - Timeout이 되었을 경우 등
- 이렇게 모아두게 되면 분석이 가능하여 sw 를 update할 수 있음
- **똑같은 Topic이나 이벤트가 들어오는지 확인을 하게 된다.**
  - 즉 이미 있는 Topic인 경우에는 바로 DLQ에 넣게 된다.



```python
import traceback

@app.task(bind=True, queue='celery')
def is_positive_number(self, num:int):
    try:
        if num < 0:
            raise ValueError()
	except Exception as e:
        traceback_str = traceback.format_exc()
        handle_error.apply_async(arg={self.request.id, str(e), traceback_str})

# 이렇게 전역으로 만들어 놓고 사용하면 될 듯
# dlq라는 queue를 따로 만들어 주어야 한다.
@app.task(queue="dlq")
def handle_error(task_id, exception, traceback_str):
    print(f"task_id {task_id}")
    print(f"exception {exception}")
    print(f"traceback_str: {traceback_str}")
```



## Time limit vs Timeout

**Time limit**

- Task parameter (time_limit)
- termination하기 전에 clean up or error handling 하려고 gracefully 하게  timeout을 handling하고 싶을 때 사용한다.
- task는 failure로 표시 된다.
- Task자체의 시간을 말한다.

**Timeout**

- AsyncResult get parameter (timeout)
- Task가 완료되고 재시도 결과를 기다린다. 
- 전체 Task가 끝나서 Retrun까지를 말한다.

```python
# Time limit
@app.task(queue='celery', time_limit=5)
def task():
    time.sleep(10) # task 자체가 fail로 뜬다.


# Timeout
def task():
    time.sleep(10)
def simulate():
    res = task()
    res.get(timeout=3)

```



## Task Callback(Linking)

```python
@app.task(queue="celery")
def error_handler(request, exc, traceback):
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
          request.id, exc, traceback))

def simulating_link():
    result = add.apply_async(
                args=[2, "error"],
                link=multiply.s(10),
                link_error=error_handler.s()) # type: ignore
    # parent result
    print(result.get())
    # child result
    print(result.children[0].get())
```



## Signal Error

```python
# Define signal handlers
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



















