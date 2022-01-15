import requests
from bs4 import BeautifulSoup

url = 'https://comic.naver.com/webtoon/weekday'  # 네이버 웹툰
res = requests.get(url)
res.raise_for_status()

soup = BeautifulSoup(res.text, "lxml") #가져온 html문서를 lxml를 통해서 Bs객체로 만든 것

# 웹 html에 대해서 잘 알 경우 이 방법을 사용하게 된다.

# print(soup.title) # title가져오기
# print(soup.title.get_text())  #타이틀에서 문자만 가져오기
# print(soup.a) # 첫번째로 발견된 정보 a를 보여줘라는 뜻
# print(soup.a.attrs) # a의 속성정보를 출력해줌
print(soup.a["href"]) # a의 href 속성 값의 정보를 얻을 수 있다.



# 잘 모를 경우 = find를 사용

# print(soup.find('a',attrs = {'class': 'Nbtn_upload' })) # class값이 'Nbtn_upload' 인 a element를 찾아줘
# print(soup.find(attrs = {'class': 'Nbtn_upload' })) # class값이 'Nbtn_upload' 인 어떤 element를 찾아줘

# print(soup.find('li', attrs = {'class' : 'rank01'}))

# rank1 = soup.find('li', attrs = {'class' : 'rank01'})
# print(rank1.a)

# # 자식부모로 가기
# print(rank1.a.get_text()) # 여신강림
# rank2 = rank1.next_sibling.next_sibling # 줄바꿈이 있는 경우 next를 두번 한다
# rank3 = rank2.next_sibling.next_sibling # 

# rank2 = rank3.previous_sibling.previous_sibling  # 뒤로가기

# rank1.parent # 부모값이 나오게 된다.

# rank2 = rank1.find_next_sibling('li') # li인 값만 나오게 된다.
# # print(rank2.a.get_text())
# rank3 = rank2.find_next_sibling('li')
# # print(rank3.a.get_text())

# 한번 찾기
# print(rank1.find_next_siblings('li'))

webtoon = soup.find('a', text = '여신강림-190화') #이부분을 가져오기
print(webtoon)

