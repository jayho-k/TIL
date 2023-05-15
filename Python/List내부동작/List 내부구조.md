# List 내부구조

**list**

- 초기 선언시 크기를 지정하지 않아도 된다.
- 자료형을 지정하지 않아도 된다.
- 여러 자료형 데이터를 저장할 수 있다.

내부 구조

<img src="./List 내부구조.assets/image-20230419163741420.png" alt="image-20230419163741420" style="zoom: 67%;" />

PyObject

- 모든 파이썬 객체들은 PyObject라는 구조체의 확장판
  - 즉 모든 객체들을 PyObject를 가지고 있다.
  - PyObject구조체에는 객체의 reference count값과 대응되는 타입의 객체를 가리키는 포인터가 있다.

```C++
typedef struct _object{
    _PyObject_HEAD_EXTRA;
    Py_ssize_t ob_refcnt;
    PyTypeObject *ob_type;
} PyObject;
```



PyVarObject

- PyObject의 확장판
  - 길이를 가진 객체에서 사용된다.
  - 따라서 ob_size필드가 추가된다.

```c++
typedef struct {
	PyObjec ob_base;
    Py_ssize_t ob_size; // 길이
} PyVarObject;
```



PyObejct_VAR_HEAD

- 인스턴스마다 길이가 변하는 객체를 선언할 때 사용



PyListObject

- PyListObject라는 구조체로 구현되어있다.
- **PyObject_VAR_HEAD**
- **ob_item** : 이중 포인터 (리스트 원소들의 포인터 배열에 대한 포인터)
- **allocated** : 리스트의 할당된 크기를 저장한다. 리스트에 담긴 원소의 수, 즉 리스트의 길이는 ob_size에 저장되므로 ob_size는 allocated보다 항상 작거나 같다.

```c++
typedef struct {
    PyObject_CAR_HEAD
	PyObjec **ob_item;
    Py_ssize_t allocated; // 길이
} PyListObject;
```

- PyListObject 코드를 통해 파이썬 리스트는 리스트 원소들의 포인터를 저장
- ob_item이라는 이중 포인터를 사용해서 해당 배열의 주소값을 저장
- 이 구조때문에 C언어의 배열보다 파이썬 리스트를 더욱 편리하게 사용할 수 있다.



C언어의 배열

- 4바이트*4만큼 메모리를 할당받아 **연속적으로 저장**
- 변수 arr은 배열의 **시작 주소를 가지고 있음**



파이썬 리스트

- ob_item이라는 이중 포인터 존재
  - ob_item은 리스트 원소들의 주소값을 저장한 c언어의 배열을 가르킨다.
  - 이 배열에 저장된 주소값을 통해 실제 원소 값에 접근할 수 있다.

<img src="./List 내부구조.assets/image-20230419165755629.png" alt="image-20230419165755629" style="zoom:67%;" />

- 파이썬은 원소의 주소값을 저장
- **즉 각 원소의 자료형이 무엇이든 상관이 없음**
  - 따라서 자료형을 따로 지정하지 않아도 된다.
- 하지만 이중포인터를 사용하기 때문에 특정 값을 찾기 위해 두 번의 탐색 과정을 거치게 된다.
  - 그결과 c언어의 배열보다 속도가 느리다.



메모리 할당

- 파이썬 : 동적 배열
  - 초기 선언시 리스트의 크기를 지정하지 않음
- 리스트가 꽉채워지면 크기를 늘려주는 방식으로 동작 ( 더블링 )
- 메모리 할당 :  list_resize 

```C++
static int
list_resize(PyListObject *self, Py_sszie_t newsize){
    PyObject **items;
    size_t new_allocated, num_allocated_bytes;
    Py_ssize_t allocated = self-> allocated;
    
    if (allocated >= newsize && newsize >= (allocated >> 1)){
        assert(self->ob_item !=NULL || newsize==0);
        Py_SET_SIZE(self, newsize);
        return 0;
    }
}
```

- allicated : 리스트의 현재 할당된 크기
- newsize : 리스트의 길이를
- 만약 리스트의 길이가 할당된 크기보다 충분히 크다면 메모리 할당을 하지 않는다.
- 리스트의 할당된 크기를 늘려주는 경우에는 현재 리스트의 길이에 비례하여 0,4,8,16, 순으로 메모리를 추가적으로 할당한다.