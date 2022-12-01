# Vue

[개발하면서 경험으로 알게 된 Vuex에서 Store활용 방법](https://ux.stories.pe.kr/149)

https://velog.io/@lsj8367/Javascript-%EB%8F%99%EA%B8%B0%EC%99%80-%EB%B9%84%EB%8F%99%EA%B8%B0%EB%B0%A9%EC%8B%9D%EC%9D%98-%EC%B0%A8%EC%9D%B4%EC%A0%90

### dispatch와 commit의 차이점

dispatch

- 비동기 동작을 포함하여 actions에 데이터를 제출 합니다.

- 배경에 데이터를 제출 할 수 있습니다



commit

- 동기화 작업

- 데이터를 mutations에 제출합니다.

- 사용자 정보를 읽고 캐시에 쓸 수 있습니다.



### vuex의 특징

- 단방향으로 관리한다는 것

각각 컴포넌트(dispatch) => actions(comimt) => mutations(state) ==> state => 모든 컴포넌트에서 활용



### 동기와 비동기 차이

동기화

- 모든 일은 순차적으로 실행되며 어떤 작업이 수행중이라면 다음 작업은 대기하게 된다.



비동기

- 비동기로 처리하지 않고 동기적으로 구성을 하게 된다면 데이터를 받아오기까지 기다린 다음에 앱이 실행될 것이고 서버에 가져오는 데이터 양이 늘어날수록 앱의 실행속도는 기하급수적으로 느려진다.

-  이런 불편을 없애기 위해서 데이터를 수신하는 코드와 페이지를 표시하는 것과는 비동기적으로 처리를 해야한다.  
  그래서 비동기처리로 가장 많이 드는 예가바로 setTimeout과 AJAX가 있다.





# Async/Await

Node.js 7.6버전부터 구현된 기능이며 `Async/Await`를 사용하면 promise에 비해 보다 쉽게 비동기적인 상황을 표현할 수 있다.

```javascript
async function f1() {
  const a = await add10(10);
  const b = await add10(a);
  console.log(a, b)
}
f1();
```

Async와 Await을 사용하려면 우선 사용할 함수 앞에 async라는 키워드를 붙여 사용해야 하며 선언된 **async 함수 안에서만 await 키워드를 사용할 수 있다.**





### Async/Await의 예외 처리

```javascript
async function f2() {
  const a = await add10(10).then(res => res);
  const b = await add10(a).catch(err => err);
  console.log(a, b)
}
f2();
```

위의 코드에선 add10()이 promise를 리턴하니까 promise가 지원하는 메소드를 사용이 가능하다. 그래서.catch()를 이용하여 예외처리를 할 수 있다.

```javascript
async function f3() {
  try {
    const a = await add10(10)
    const b = await add10(a)
    console.log(a, b)
  } catch(err) {
    console.log(err)
  }
}
f3();
```

이렇게 기존방식인 `try-catch`도 사용이 가능하다.


