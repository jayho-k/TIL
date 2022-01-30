# headless크롬을 사용할 때 주의 할 점
# 긁어 올때 거부될 수 있음
# 공부를 더 하고 싶을 경우 selenium with python을 치셈
from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.headless = True

# 눈에 보이지는 않지만 백그라운드에서 웹브라우저에 크기를 조절해줄 수 있다.
options.add_argument('window-size=1920x1080') #띄어쓰기를 하면 안된다// agent하는 방법
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36')

browser = webdriver.Chrome('C:\ProgramData\Anaconda3\Python Workspace\chromedriver_win32/chromedriver.exe', options = options)
url = 'https://www.whatismybrowser.com/detect/what-is-my-user-agent'
browser.get(url)

detected_value = browser.find_element_by_id('detected_value')
print(detected_value.text)

browser.quit()

# 
