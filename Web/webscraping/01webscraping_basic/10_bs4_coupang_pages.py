# 9 + 여러페이지 수에서 사용
import requests
import re
from bs4 import BeautifulSoup

headers = {"User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

for i in range(1,6):
    print('페이지:', i)
    url = 'https://www.coupang.com/np/search?q=%EB%85%B8%ED%8A%B8%EB%B6%81&channel=user&component=&eventCategory=SRP&trcid=&traid=&sorter=scoreDesc&minPrice=&maxPrice=&priceRange=&filterType=&listSize=36&filter=&isPriceRange=false&brand=&offerCondition=&rating=0&page={}&rocketAll=false&searchIndexingToken=1=5&backgroundColor='.format(i)

    res = requests.get(url, headers = headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")
    items = soup.find_all('li', attrs= {'class' : re.compile('^search-product')})
    # 앞에 search-product가 들어간 것으로 형태를 잡음

    # print(items[0].find('div', attrs = {'class':'name'}).get_text())

    # 원하는 데이터 끌고오기
    for item in items:
        name = item.find('div', attrs= {'class':'name'}).get_text() # 제품명

        # 애플제품 제외
        if 'Apple' in name:
            #print('애플상품 제외')
            continue
        
        #가격
        price = item.find('strong', attrs = {'class' : 'price-value'}).get_text() 


        # 평점 // 리뷰 100개이상, 평점 4.5이상 되는 것만 조회
        rate = item.find('em', attrs = {'class' : 'rating'})
        if rate:
            rate = rate.get_text()
        else:
            #print('평점 없으면 제외함')
            continue

        # 평점수
        rate_cnt = item.find('span', attrs = {'class' : 'rating-total-count'})
        if rate_cnt:
            rate_cnt = rate_cnt.get_text()
            rate_cnt = rate_cnt[1:-1]  # 값: (26)이기 때문에 괄호를 없애기 위함
        else:
            #print('평점 없으면 제외함')
            continue
        
        link = item.find('a', attrs = {'class' : 'search-product-link'})['href'] # 링크가져로기

        if float(rate) > 4.5 and int(rate_cnt) >= 100:
            print(f'제품명: {name}')
            print(f'가격: {price}')
            print(f'평점: {rate}점, ({rate_cnt}개)')
            print('바로가기: {}'.format('https://www.coupang.com'+link))
            print('-'*100)

        
        # # 광고제품 제외
        # ad_bg = item.find('span', attrs = {'class' : 'ad-badge-text'})
        # if ad_bg:
        #     print('광고상품 제외')
        #     continue
        # print(name, price, rate, rate_cnt)






