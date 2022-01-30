import requests
from bs4 import BeautifulSoup
import csv

# 거래: 매매/ 면적 () / 가격 ()/ 동/ 층

url = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=%EC%86%A1%ED%8C%8C+%ED%97%AC%EB%A6%AC%EC%98%A4%EC%8B%9C%ED%8B%B0+%EB%A7%A4%EB%AC%BC&oquery=%EC%86%A1%ED%8C%8C+%ED%97%AC%EB%A6%AC%EC%98%A4%EC%8B%9C%ED%8B%B0+%EB%A7%A4%EB%AC%BC&tqi=hPncGlp0J14ssnIu2oZssssssjs-260688'
res = requests.get(url)
res.raise_for_status()

filename = '매매.csv'
f = open(filename, 'w', encoding= 'utf-8-sig')
writer = csv.writer(f)

soup = BeautifulSoup(res.text, 'lxml')

title = '거래	소재지	단지명제공	면적	매물가	층	네이버'.split('\t')

data_rows = soup.find('table', attrs = {'class':'list'}).find('tbody').find_all('tr', {'class':'_land_tr_row'})

writer.writerow(title)

for row in data_rows:
    columns = row.find_all('td')
    # naver = row.find('td', attrs = {'class': 'fs provider'})
    data = [column.get_text() for column in columns]

    # print(data)
    writer.writerow(data)

