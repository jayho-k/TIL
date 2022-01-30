from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome('C:\ProgramData\Anaconda3\Python Workspace\chromedriver_win32/chromedriver.exe')
# browser.maximize_window() # 창 최대화

url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_sug.pre&fbm=1&acr=1&acq=%EB%84%A4%EC%9D%B4%EB%B2%84+%ED%95%AD&qdt=0&ie=utf8&query=%EB%84%A4%EC%9D%B4%EB%B2%84+%ED%95%AD%EA%B3%B5%EA%B6%8C'
browser.get(url)

time.sleep(10)

# browser.find_element_by_class_name('sp_flight flight_btn_txt').click()

# # # # 이번달 27일, 28일 선택 
# browser.find_element_by_link_text('27')[0].click()
# browser.find_element_by_link_text('28')[1].click()

# browser.find_element_by_xpath('//*[@id="__next"]/div/div[1]/div[7]/div/ul/li[1]/button/figure/img')

# #항공권 검색
# browser.find_element_by_link_text('')

# //*[@id="__next"]/div/div[1]/div[4]/div/div/div[2]/div[2]/button[2]



# element가 나올때까지만 기다리게 할 수 있음
# 브라우저 10초 기달 ==> 저 xpath값이 나올때 까지
try:
    elem = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "")))
    print(elem.text)

finally:
    browser.quit()

