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



































