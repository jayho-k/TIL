import requests
from bs4 import BeautifulSoup

url = 'https://search.daum.net/search?w=tot&q=2019%EB%85%84%EC%98%81%ED%99%94%EC%88%9C%EC%9C%84&DA=MOR&rtmaxcoll=MOR'
res = requests.get(url)
res.raise_for_status()

soup = BeautifulSoup(res.text, 'lxml')

images = soup.find_all('img', attrs = {'class':'thumb_img'})

for year in range(2015, 2020):
    url = 'https://search.daum.net/search?w=tot&q={}%EB%85%84%EC%98%81%ED%99%94%EC%88%9C%EC%9C%84&DA=MOR&rtmaxcoll=MOR'.format(year)
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')

    images = soup.find_all('img', attrs = {'class':'thumb_img'})

    for idx, image in enumerate(images):
        image_url = image['src']  # src --> class 옆에 있는 속성
        if image_url.startswith('//'):  # //로 시작한다면
            image_url = 'http:' + image_url # http를 붙이셈

        print(image_url)
        image_res = requests.get(image_url)
        image_res.raise_for_status()

        with open('movie_{}_{}.jpg'.format(year,idx+1), 'wb')as f:
            f.write(image_res.content)   # w= 글자, wb = 글자아님

        if idx >= 4:
            break