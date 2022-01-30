# 더 공부문제: 구글에 beautifulsoup참고

import requests
from bs4 import BeautifulSoup

url = 'https://comic.naver.com/webtoon/list?titleId=675554'
res = requests.get(url)
res.raise_for_status()

soup = BeautifulSoup(res.text, "lxml")

# 현재 a element에 정보가 없는 상태 // table로 이루워진 상태
# 따라서 그 위에 class를 이용해서 스크래핑을 할 생각
# a태그 밑에 있는 text를 가져오는 것
# cartoons = soup.find_all("td", attrs={'class': 'title'} )
# title = cartoons[0].a.get_text()
# 링크로 들어가기까지 할 생각
# 앞정보는 빠진 상태가 되었음
# link = cartoons[0].a['href']
# print(title)
# print('https://comic.naver.com' + link) # 링크로 갈수 있음

# 만화제목 + 링크 가져오기
# for cartoon in cartoons:
#     title = cartoon.a.get_text()
#     link = 'https://comic.naver.com' + cartoon.a['href']
#     print(title, link)


# 
# 평점 정보 빼오기+ 평균 평점계산하기
total_rate = 0
cartoons = soup.find_all('div', attrs= {'class': 'rating_type'})
for cartoon in cartoons:
    rate = cartoon.find('strong').get_text()  # ???? 뭐니????
    print(rate)
    total_rate += float(rate)

print('전체 점수:', total_rate)
print('평균 점수 :', total_rate/ len(cartoons))