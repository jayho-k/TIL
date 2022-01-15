# 상황: 노트북 구매, 광고 제외, 평점 높은 것을 사고싶음
# 페이지를 넘기고 싶은데 주소창을 보니 page=1이라는 문구가 있음

# get = 
# http..........?물음표가 붙음 &표시로 구분
# 데이터의 양이 정해져 있음
# url만 조작하면 됨

# post = 
# ? id = & pw= 
# 크기가 큰 파일도 보낼 수 있음

import requests
import re
from bs4 import BeautifulSoup

# user 권한을 이용해서 해주어야 한다.

url = 'https://www.coupang.com/np/search?q=%EB%85%B8%ED%8A%B8%EB%B6%81&channel=user&component=&eventCategory=SRP&trcid=&traid=&sorter=scoreDesc&minPrice=&maxPrice=&priceRange=&filterType=&listSize=36&filter=&isPriceRange=false&brand=&offerCondition=&rating=0&page=1&rocketAll=false&searchIndexingToken=1=5&backgroundColor='
headers = {"User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
res = requests.get(url, headers = headers)
res.raise_for_status()
soup = BeautifulSoup(res.text, "lxml")
items = soup.find_all('li', attrs= {'class' : re.compile('^search-product')})
# print(items[0].find('div', attrs = {'class':'name'}).get_text())

# 원하는 데이터 끌고오기
for item in items:
    name = item.find('div', attrs= {'class':'name'}).get_text() # 제품명

    # 애플제품 제외
    if 'Apple' in name:
        print('애플상품 제외')
        continue

    price = item.find('strong', attrs = {'class' : 'price-value'}).get_text() #가격


    # 평점 // 리뷰 100개이상, 평점 4.5이상 되는 것만 조회
    rate = item.find('em', attrs = {'class' : 'rating'})
    if rate:
        rate = rate.get_text()
    else:
        print('평점 없으면 제외함')
        continue

    # 평점수
    rate_cnt = item.find('span', attrs = {'class' : 'rating-total-count'})
    if rate_cnt:
        rate_cnt = rate_cnt.get_text()
        rate_cnt = rate_cnt[1:-1]  # 값: (26)이기 때문에 괄호를 없애기 위함
    else:
        print('평점 없으면 제외함')
        continue

    if float(rate) > 4.5 and int(rate_cnt) >= 100:
        print(name, price, rate, rate_cnt)
    
    # # 광고제품 제외
    # ad_bg = item.find('span', attrs = {'class' : 'ad-badge-text'})
    # if ad_bg:
    #     print('광고상품 제외')
    #     continue
    # print(name, price, rate, rate_cnt)






