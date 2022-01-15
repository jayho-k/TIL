import requests
from bs4 import BeautifulSoup

# 웹툰의 모든 정보를 가져온다

url = 'https://comic.naver.com/webtoon/weekday'  # 네이버 웹툰
res = requests.get(url)
res.raise_for_status()

soup = BeautifulSoup(res.text, "lxml")

# class가 title인 것을 가져올 것

#모든 웹툰이름의 정보를 가져온다
cartoons = soup.find_all('a', attrs = {'class': 'title'})
# a element 의 class 속성이 title인 'a' element를 반환
for cartoon in cartoons:
    print(cartoon.get_text())


