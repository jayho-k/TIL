## Pandas

**시리즈(Series)**

1. t = pd.Series([-20,-10,10,20]) # 시리즈로 만들어주기

   t[0] 가능

2. temp = pd.Series([-20,-10,10,20], **index = ['1월','2월','3월','4월']**)

   인덱스 따로 가능

   

## DataFrame

​	**pd.DataFrame(data, index ,columns )**

1. **df = pd.DataFrame(data**) 이렇게 생성

   data 는 딕셔너리로

	2. df = pd.DataFrame(data, index = list(range(1,9))) **인덱스 추가 가능**

​		df = pd.DataFrame(data, index = ['1번','2번','3번','4번','5번','6번','7번','8번'])

3. 칼럼 지정

   df = pd.DataFrame(data, columns = ['이름', '학교', '키']) 순서도 바꿀수 있다



## 인덱스

- **df.index.name** = '지원 번호'  : 인덱스 이름 설정
- **df.reset_index()** : 초기화 (인덱스  0~n) 을 추가하면서 초기화(원래 있던 1번 .. 살아있음)

- **df.reset_index(drop = True, inplace =Ture)**  # 원래 쓰던 것을 삭제// 저장을 안해줌
- **df.set_index('이름')** : 이름을 인덱스로 설정
- df.sort_index() # 오름차순/ df.sort_index(ascending = False) #내림



## 저장하기

- df.to_무언가('파일이름', 인코딩)

- df.to_csv('score.csv', encoding = 'utf-8-sig')    csv

- df.to_csv('score.txt', sep = '\t')# 역슬레시 + 텝 메모

- df.to_excel('score.xlsx') 엑셀

  

## 파일열기

- df = pd.read_무언가('파일 이름')

  

- df = pd.read_csv('score.csv', skiprows = 1) 

  - 1개 로우를 무시하는 것 (지정된 개수 만큼의 로우를 제거)

  - df = pd.read_csv('score.csv', skiprows = [1,3,5])  # 1 3 5 제거

  - df = pd.read_csv('score.csv', nrows = 4)  # 4개 가져와

  - df = pd.read_csv('score.csv', skiprows = 2, nrows = 4)  # 처음 2개는 무시,  4개 가져와

    

- df = pd.read_csv('score.txt', sep = '\t')

  - df = pd.read_csv('score.txt', sep = '\t', index_col = '지원번호') # 지원번호를 인뎃스로 저장

    

- df = pd.read_excel('score.xlsx', index_col = '지원번호')



## 데이터 확인

- df.describe() # 개수, 평균, 표준편차, 최소, 최대등 을 계산해 준다
- df.info() # 타입 들을 보여준다
- df.head()
- df.tail()
- df.values : 말그대로 벨류들을 나열해준다
- df.index
- df.columns
- df.shape



각각을 확인할 때

- df['벨류 타이틀을 적는다'].describe()

- df['키'].describe()  #키에서 많은 정보를 보여줌
- df['키'].min() 등등등
- df['키'].nlargest(3)  # 키가 큰 순서대롤 3명만 뽑아줘1! 라는 뜻 // 라지스트
- df['SW특기'].count() 
- df['학교'].unique()  # 중복을 제외한 값을 출력하게 된다.  (집합처럼)























