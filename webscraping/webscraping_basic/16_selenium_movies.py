from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup

browser = webdriver.Chrome('C:\ProgramData\Anaconda3\Python Workspace\chromedriver_win32/chromedriver.exe')
url = 'https://play.google.com/store/movies/collection/cluster?clp=0g4XChUKD3RvcHNlbGxpbmdfcGFpZBAHGAQ%3D:S:ANO1ljJvXQM&gsr=ChrSDhcKFQoPdG9wc2VsbGluZ19wYWlkEAcYBA%3D%3D:S:ANO1ljK7jAA&hl=ko&gl=US'
browser.get(url)
browser.maximize_window()

# 스크롤 내리기
# 해상도의 높이인 1080위치로 스크롤 내리기 (지정한 위치에 스크롤 내리기)
# browser.execute_script('window.scrollTo(0, 2080)') # 1920 X 1080 

# # 화면 가장 아래로 스크롤 내리기
# browser.execute_script('window.scrollTo(0, document.body.scrollHeight)') # 현재 문서 총높이

interval = 3

# 현재 문서 높이를 가져와서 저장(리턴)
prev_height = browser.execute_script('return document.body.scrollHeight')

while True:
    # 스크롤 내리기
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')

    # 5초 대기
    time.sleep(interval)

    # 현재 문서 높이를 가져와서 저장
    curr_height = browser.execute_script('return document.body.scrollHeight')

    # 스크롤이 끝까지 내려갔을 때 멈춰라
    if curr_height == prev_height:
        break

    prev_height = curr_height
print('종료')


soup = BeautifulSoup(browser.page_source, "lxml")

# movies =  soup.find_all('div', attrs = {'class':['ImZGtf mpg5gc','Vpfmgd']})
movies =  soup.find_all('div', attrs = {'class':'Vpfmgd'})
# 리스트로 감싸면 둘 중 하나 있으면 가져와

# 타이틀 정보가져오기// 할인된 영화만 찾기
for movie in movies:
    title = movie.find('div', attrs = {'class':'WsMG1c nnK0zc'}).get_text()


    # 할인전 가격
    original_price = movie.find('span', attrs = {'class':'SUZt4c djCuy'})
    if original_price:
        original_price = original_price.get_text()
    else:
        # 할인되지 않은 가격은 제외
        continue
    
    # 할인된 가격
    price = movie.find('span', attrs = {'class':'VfPpfd ZdBevf i5DZme'}).get_text()

    # 링크
    link = movie.find('a', attrs = {'class':'JC71ub'})['href']
    # https://play.google.com/ + link

    print(f'제목: {title}')
    print(f'할인전 가격: {original_price}')
    print(f'할인된 가격: {price}')
    print('링크 :', 'https://play.google.com/' + link)
    print('-'*100)
