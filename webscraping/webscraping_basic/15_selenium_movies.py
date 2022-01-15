# 동적페이지 정보가져오기

from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup


headers = {
    "User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    # ,'Accept_Language' : 'ko-KR,ko' #한글로 된 홈피 있으면 보여줘
}
url = 'https://play.google.com/store/movies/collection/cluster?clp=0g4XChUKD3RvcHNlbGxpbmdfcGFpZBAHGAQ%3D:S:ANO1ljJvXQM&gsr=ChrSDhcKFQoPdG9wc2VsbGluZ19wYWlkEAcYBA%3D%3D:S:ANO1ljK7jAA&hl=ko&gl=US'
res = requests.get(url, headers = headers)
res.raise_for_status()

soup = BeautifulSoup(res.text, "lxml")

movies =  soup.find_all('div', attrs = {'class':'ImZGtf mpg5gc'})
print(len(movies))

# 타이틀 정보가져오기
for movie in movies:
    title = movie.find('div', attrs = {'class':'WsMG1c nnK0zc'}).get_text()
    print(title)

#스크롤을 내릴때 마다 새로운 정보를 주게된다.



# soup.prettify() # 이쁘게 html을 보여줌