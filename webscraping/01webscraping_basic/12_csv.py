# 네이버 시총 긁어오기
import csv
import requests
from bs4 import BeautifulSoup

url = 'https://finance.naver.com/sise/sise_market_sum.nhn?&page='

filename = '시가총액 1~100.csv'
f = open(filename, 'w', encoding = 'utf-8-sig', newline='')  # newline을 쓰는 이유는 공백을 없애기 위해
writer = csv.writer(f)

title = 'N	종목명	현재가	전일비	등락률	액면가	시가총액	상장주식수	외국인비율	거래량	PER	ROE	토론실'.split('\t')
# [n, 종목명 현재가 ...]
writer.writerow(title)

for page in range(1,5):
    res = requests.get(url+str(page))
    res.raise_for_status()

    soup = BeautifulSoup(res.text, 'lxml')

    data_row = soup.find('table', attrs = {'class':'type_2'}).find('tbody').find_all('tr')

    for row in data_row:
        columns = row.find_all('td')
        if len(columns) <= 1:
            continue
        data = [column.get_text().strip() for column in columns]  # strip: 공백제거
        #print(data)
        writer.writerow(data)
    