from selenium import webdriver
import time


# 네이버 로그인
browser = webdriver.Chrome('C:\ProgramData\Anaconda3\Python Workspace\chromedriver_win32/chromedriver.exe')
browser.get('http://naver.com')

elem = browser.find_element_by_class_name('link_login')
elem.click()

browser.find_element_by_id('id').send_keys('asd')
browser.find_element_by_id('pw').send_keys('asd')

time.sleep(1)

browser.find_element_by_id('log.login').click()

# html 정보 출력
print(browser.page_source)

# 종료
# browser.close()
browser.quit()
