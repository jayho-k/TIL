# int와  Integer차이

## int : 자료형 : 

- 평소에 사용
- null로 초기화 불가
- int의 정수 값을 다른 기본으로 변환할 수 없음
- 4바이트 필요



## Integer  :wrapper클래스 

- Unboxing 하지 않을 시 산술 연산 불가능
- null값 처리 가능
- toBinaryString, toOctalString, toHexString 함수를 사용하면서 각각 2진수, 8진수, 16진수로 변환할 수 있음 ==> 즉 함수를 사용할 수 있음
- null값을 사용할 때 또는 클래스로 비교해야할 떄 사용
- equal을 사용해야한다. ==> 즉 주소값으로 비교하면 안된다는 뜻
- 제네릭 타입은 래퍼 클래스만 들어갈 수 있다. 
- 





