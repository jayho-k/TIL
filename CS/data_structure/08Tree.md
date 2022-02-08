# Tree

## 1. 소개

연결리스트: 자식이 하나 밖에 없는 Tree이다  (일직선으로 되어 있기 때문에)

- Tree: 자식과 부모가 있는 무언가

- 이진트리: 하나의 부모가 2개의 자식까지 있는 모양(가장 간단하면서 많이 쓰이는 구조)

![image-20220208215823541](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220208215823541.png)

- 높이: 
  - 가장 높은 노드부터 leaf node까지 몇개의 링크가 있는지
  - 높이 = 레벨

- 경로(path): ex) 3 => 2 => 7 => 8 => 12
  - 어떤 노드에서 원하는 노드까지의 길

- 경로 길이(path length):  ===> 4
  - 엣지의 개수



### 표현법



![image-20220208220618523](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220208220618523.png)

- 표현법1: 리스트:  => level0 =>  level1=> level2 => .....  
  - 비어있으면 빈값으로 냅둔다 (None)
  - A = [a, b, c, None, d, e, f, None, None, h, i , g]



![image-20220208221208884](C:\Users\JHK_ssafy\AppData\Roaming\Typora\typora-user-images\image-20220208221208884.png)

- 표현법2: 리스트 (재귀적으로 표현)
  - [a,[a의 왼쪽 부트리], [a의 오른쪽 부트리]]
  - a의 왼쪽=>[b , [  ] , [ d , [  ] , [  ]  ] ]     ///  a의 오른쪽=> [c, [ e , [  ]  ,[  ] ] , [ f ,  [  ] , [  ] ] ]
  - 위에 것을 다 합치면 된다.



- 표현법 3: 노드 class: 직접 노드 정의
  - key에서 두개의 멤버를 표현할 수 있도
  - 거기다가 parants를 또 만들수 있음
  - 총 key 값, parents. left, right 이렇게 기본 4개가 필요함











