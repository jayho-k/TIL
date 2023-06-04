# 02_C_basic2



## 01_2차원 배열

```c
int main(){
    int arr[2][3];
    
    int arr[2][3]  = {
        {1,2,3},
        {4,5,6}
    };
}
```

**이차원 배열 크기 구하기**

```c
#include <stdio.h>

int main()
{
	int tarr[3][4] =
	{
		{1, 2, 3, 4},
		{5, 6, 7, 8},
		{9, 10, 11, 12}
	};
    // 크기
	int y = sizeof(tarr)/sizeof(tarr[0]);
	int x = sizeof(tarr[0])/sizeof(int);
		
	for(int i=0; i<y; i++)
	{
		for (int j=0; j<x; j++)
		{
			printf("%d ", tarr[i][j]);
		}
		printf("\n");
	}
	
	return 0;
}
```





## switch문

- if 문처럼 관계시을 쓰지는 못한다. => **특정한 정수값이나 문자**만 확인가능
  - 실수 값의 경우 오류가 발생

- if 문 처럼 조건을 체크하면서 내려가지 않음  ==> **입려받은 값의 케이스로 바로 이동**
  - 일반적으로 4개 이상의 조건일 때 **switch문을 사용하면 성능이 더 좋다고 한다.**
  - 어셈블리쪽 코드상의 차이라고 한다.

```c
switch(기준값)
{
	case 비교값1:
		기준값과 비교값1이 같을 때 실행
         break
            
	case 비교값2:
    case 비교값3: // 이렇게 진행되면 2~3까지가 가능하다 왜냐하면 break가 없기 때문
		기준값과 비교값2가 같을 때 실행
         break
	
	default:
		기준값과 비교값들이 같지 않을 때 실행
}
```

- 필요한 값만 실행해주기 위해선 break를 걸어주어야한다 



## 두 변수의 값 바꾸기

```c
#include <stdio.h>

int main()
{
	int a = 5;
	int b = 10;

	a = b; // a값 10
	b = a; // b값 10 ==> 따라서 10,10값이 나타난다.
	return 0;
}
```

```c
#include <stdio.h>

int main()
{
	int a = 5;
	int b = 10;
	int temp;

	temp  = a; // 따라서 tmp값을 통해서 값을 저장해준다.
	a = b;
	b = temp;
	return 0;
}
```





## 함수

### 함수의 선언

- c언어는 절차지향언어
  - 즉 위에서 마래로 차례대로 소스코드를 해석한다.
  - 따라서 main() 함수가 가장 아래 있어야 한다는 뜻

```c
#include <stdio.h>

int func1(void); // 이 함수 먼저 정의 => 원형을 먼적 정의해준다.

int main()
{
	func1();
	printf("함수 실행 완료\n");
	return 0;
}

int func1(void)
{
	printf("예시 함수입니다.\n");
	return 0;
}
```





### 전역 변수와 지역변수

- 전역변수의 단점
  - 프로그램이 복잡할 수록 어떤 함수에서 전역변수의 값을 바꾸는지 알기 어려워진다.
  - 지역변수와 전역변수 중에서 같은 변수가 있는 경우
    - **지역변수를 우선적으로 접근**





## 포인터

- 주소를 가르키는 것

```c
#include <stdio.h>

int main()
{
	int *p = NULL;  // int* p == int * p 모두 같음
	int num = 15;

	p = &num;

	printf("int 변수 num의 주소 : %d \n", &num);
	printf("포인터 p의 값 : %d \n", p);
	printf("포인터 p가 가리키는 값 : %d \n", *p);

	return 0;
}
// int 변수 num의 주소   : 1985123123
// 포인터 p의 값         : 1985123123
// 포인터 p가 가리키는 값 : 15
```

- *(참조 연산자) : 선언

- 포인터의 크기는 모두 동일

  - 32비트 = 4byte

  - 32비트 = 8byte

    

- 포인터 초기화 : int *p = NULL(0);

  - **0은 0번지를 가르키는 것이 아니라 아무것도 없다는 뜻**

- 주소값을 넣을 떄 : p = &num

<img src="02_C_basic2.assets/image-20230529001043746.png" alt="image-20230529001043746" style="zoom: 67%;" />

- 포인터에 num을 저장
  - 그럼 주소 값 1000이 저장되게 된다.
  - 주소 값 1000에는 num값이 들어 있다.





### 참조 연산자 *

- \* 연산자가 붙으면 **주소로 찾아간다**로 이해하면 좋음

```c
#include <stdio.h>

int main()
{
	int *p = NULL; 
	int num = 15;

	p = &num;
	printf("포인터 p가 가리키는 값 : %d\n", *p);
	printf("num의 값 : %d\n\n", num);

	(*p)++;
	printf("포인터 p가 가리키는 값 : %d\n", *p); // 16
	printf("num 값 : %d\n\n", num); // 16

	*p++;
	printf("포인터 p가 가리키는 값 : %d\n", *p); // -13213123
	printf("num 값 : %d\n", num); // 16

	return 0;
}
```

- (*p)++; 와 *p++; 의 차이점
  - 증감 연산자가 참조 연산자(*)보다 우선순위가 높다
  - 따라서 주소에 ++가 먼저 되고 포인트를 찍는 것
- **즉 (*p)++ 로 해주어야한다.**



### Call by Value 와  Call by reference

> - 인자를 전달하는 방식 2가지
>   - Call by Value 
>   - Call by reference

**Call by Value **

- **함수에서 값을 복사해서 전달하는 방식** 
  - => 인자로 전달되는 변수를 함수의 매개변수에 복사한다.
    - 즉 함수 int somehign( int a, int b) 에 a,b를 복사한다는 뜻
  - 즉 이렇게 복사되면 인자로 전달한 변수와는 별개의 변수가 되며, 매개변수를 변경해도 원래 변수에는 영향을 미치지 않는다.
  - 원본값을 바꿀 필요가 없는 경우에는 call by value방식을 이용

```c
# include <stdio.h>

void swap(int a, int b){
    int tmp;
    tmp = a;
    a = b;
    b = tmp;
}

int main(){
    int a, b;
   	a = 10;
    b = 20;
    
    printf("스왑 전 %d %d",a,b); // 10, 20
    swap(a, b);
    printf("스왑 전 %d %d",a,b); // 10, 20
}
```

- 즉 원본 값이 바뀌지 않는 것을 볼 수 있다.
  - **이유 swap을 진행해도 매개변수가 바뀌는 것** 



**call by reference**

- 함수에서 값을 전달하는 대신 **주소값을 전달하는 방식**
  - c언어에서는 call by reference를 공식적으로 지원하지 않는다.
  - 하지만 일반적으로 포인터를 이용해 주소값을 넘겨주는 방식을 call by reference라고 설명하는 곳이 많다.
  - 하지만 주소값을 복사해서 넘겨주는 것이기 때문에 call by value , call by address방식이라고 한다.

```c
#include <stdio.h>

void swap(int *a, int *b)
{
	int temp;

	temp = *a;
	*a = *b;
	*b = temp;
}

int main()
{
	int a, b;

	a = 10;
	b = 20;

	printf("swap 전 : %d %d\n", a, b); // 10 20
	swap(&a, &b);
	printf("swap 후 : %d %d\n", a, b); // 20 10

	return 0;
}
```





### 포인터 연산과 배열

```c
#include <stdio.h>

int main()
{
	int arr[5] = {10, 20, 30, 40, 50};
	int *arrPtr = arr;

	printf("%d\n", *arrPtr); // 10
	printf("%d\n", arr[0]); // 10

	return 0;
}

// 결과 : 10 10
    
```

- **배열의 주소값 = 첫번째 요소의 주소값**
- 따라서 & 연산자를 사용하지 않아도 arr 이름 자체가 수소값이기 때문에, 바로 포인터에 대입이 가능
  - 따라서 문자열에서는 &를 안붙혀도 되는 것



### 포인터 연산

```c
#include <stdio.h>

int main()
{
	int arr[5] = {10, 20, 30, 40, 50};
	double arr2[5] = {10.1, 20.2, 30.3, 40.4, 50.5};
	int *arrPtr = arr;
	double *arrPtr2 = arr2;

	printf("포인터 주소 : %d %d\n", arrPtr++, arrPtr2++); // 1. 주소1, 주소2
	printf("증가 연산 후 : %d %d\n", arrPtr, arrPtr2); // 2. 주소1 + 4, 주소2 + 8 
	printf("변수 값 : %d %.2f\n", *arrPtr, *arrPtr2); // 3. 20, 20.2

	arrPtr += 2;
	arrPtr2 += 2;

	printf("증가 연산 후 : %d %d\n", arrPtr, arrPtr2); // 주소1 + 4*3, 주소2 + 8*3
	printf("변수 값 : %d %.2f\n", *arrPtr, *arrPtr2); // 40, 40.4

	return 0;
}
```

1. 주소1, 주소2
2. 주소1 + 4, 주소2 + 8 
   - 이유 : int = 4, double = 8비트
3. 20, 20.2
   - 다음 요소로 간 것



\+ 버블 솔트

```c
#include <stdio.h>

void bubbleSort(int *arrPt, int n) // 주소 값의 요소를 가르키는 것
{
	int temp;	
	for(int i=0; i<n; i++)
	{
		for(int j=0; j<n-i-1; j++)
		{
			
			if(arrPt[j]>arrPt[j+1])
			{
				temp = arrPt[j];
				arrPt[j] = arrPt[j+1];
				arrPt[j+1] = temp;
			}
		}		
	}
}

int main()
{
	int arr[10];
	int n = sizeof(arr)/sizeof(arr[0]);
	for(int i=0; i<10; i++)
	{
		scanf("%d", &arr[i]);
	}

	bubbleSort(arr,n); // 배열의 주소값 = arr

	for(int i=0; i<10; i++)
	{
		printf("%d ", arr[i]);
	}
	
	return 0;
}
```



### 상수 포인터

**포인터가 가르키는 변수를 상수화** == **const int *ptr2 = \&num;**

```c
#include <stdio.h>

int main()
{
	int num = 10;
	int *ptr1 = &num;
	const int *ptr2 = &num; // 이부분 : 포인터가 가르키는 부분을 변하게 하지 않겠다는 뜻

	*ptr1 = 20;
	num = 30;

	*ptr2 = 40; // 여기서 에러가 나게 된다. ==> 즉 변수값을 바꿀 수 없음

	return 0;
}
```



**포인터 상수화**

```c
#include <stdio.h>

int main()
{
	int num1 = 10, num2 = 20;
	int *ptr1 = &num1;
	int* const ptr2 = &num1; // 이부분 
    // : 이 포인터가 오로지 num1변수만을 가르키겠다, 다른 변수를 가르키지 않겟다는 뜻
	
	ptr1 = &num2;
	
	*ptr2 = 30;
	ptr2 = &num2;
	
	return 0;
}
```

- 포인터를 상수화 시킬때에는 **const전에 *연산자 사용해야함**
- 포인터가 가르키고 있는 주소값을 변경하는 것이 불가능



### 이중 포인터

- 파이썬의 리스트 구현이 이중 포인터로 되어있음

```c
#include<stdio.h>

int main(){
    int num = 10;
    int *prt;
    int *pprt;
    
    prt = &num;
    pprt = &prt;
}
*prt == **pprt
```

- 포인터의 주소값을 담는 주소를 바꿀때
- 함수에서 문자열을 바꿀 때 사용



### 포인터 배열

```c
#include <stdio.h>

int main(){
    int num1 = 10, int num2 = 20, int num3 = 30;
    int *parr[3];
    
    parr[0] = &num1;
    parr[1] = &num2;
    parr[2] = &num3;
    
    for (int i=0; i<3; i++){
        printf("%d", i, *parr[i]); // 10 20 30
    }
}
```

- 포인터들을 저장시켜놓은 것





## 구조체



### typedef

```c
#include <stdio.h>

// 구조체 사용 form
typedef struct {
	int age;
	char phone_number[14];
} Student;

int main(){
    // 정의
	Student goorm;  
	
    // 저장 &goorm.age
	printf("나이 : ");
	scanf("%d", &goorm.age); 
	printf("번호 : ");
	scanf("%s", goorm.phone_number);
	
    // 사용 goorm.age, goorm.phone_number
	printf("----\n나이 : %d\n번호 : %s\n----", goorm.age, goorm.phone_number);
	
	return 0;
}
```



### 구조체 배열

```c
#include <stdio.h>

// 구조체
typedef struct
{
	char name[15];
	int kor; // 국어
	int eng; // 영어
	int math; // 수학
	float avg; // 평균
} Student;

int main()
{	
    // 정의
	Student sArr[3];
	
	for(int i=0; i<3; i++)
	{
        // 배열의 저장
		scanf("%s",sArr[i].name);
		scanf("%d",&sArr[i].kor);
		scanf("%d",&sArr[i].eng);
		scanf("%d",&sArr[i].math);
		sArr[i].avg = (sArr[i].kor+sArr[i].eng+sArr[i].math)/3.00;
	}
	
    // 구조체 사용
	for(int i=0; i<3; i++)
	{
		printf("%s ",sArr[i].name);
		printf("%.1f",sArr[i].avg);
		printf("\n");
	}
	return 0;
}
```





### 구조체  포인터

```c
#include <stdio.h>

typedef struct {
	int s_id;
	int age;
} Student;

int main(){
	Student goorm;
	Student *ptr;
	
	ptr = &goorm; // 정의
	
    // 이렇게 point로 사용가능
	(*ptr).s_id = 1004;
	(*ptr).age = 20;
    
    // 화살표 가능
    ptr -> s_id = 1004;
	ptr -> age = 20;
	
	printf("goorm의 학번 : %d, 나이: %d\n", goorm.s_id, goorm.age);
    // 결과 1004 , 20
}
```

- 괄호를 해야한다. => 따라서 



### 중첩 구조체

- Student 안에 Teachr 구조체 이용가능

```c
#include <stdio.h>

typedef struct {
	char name[15];
	int age;
} Teacher;

typedef struct {
	char name[15];
	int age;
	Teacher teacher;  // 이 부분
} Student;

int main(){
	Student Student;
	Teacher Teacher;
	
	Student.teacher.age = 30; // 사용시
	Teacher.age = 40;
	
	return 0;
}
```



### 자기 참조 구조체

```c
typedef struct {
	char name[15];
	int age;
	struct Student *ptr;  // 자기 자신을 참조
} Student;
```

- 연결 리스트
- 트리 등을 사용할 때 사용된다.



### 구조체 전달

```c
#include <stdio.h>

typedef struct {
	int s_id;
	int age;
} Student;


void print_student(Student *s){ // 이부분 전달 받음
	s.s_id = 2000;
	s.age = 25;
	
	printf("학번 : %d, 나이 : %d\n", s.s_id, s.age);
}

int main(){
	Student s;

	s.s_id = 1000;
	s.age = 20;
	
	print_student(&s); // 이부분 전달
    
	printf("학번 : %d, 나이: %d\n", s.s_id, s.age);
}
```

- call by value로도 가능하다 하지만 구조체 크기가 커질 수록 복사할 공간이 많이 필요하게 된다
- 따라서 call by reference를 사용한다.





