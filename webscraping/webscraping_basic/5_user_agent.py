# 권한이 걸려있는 것 뚫는 법

import requests

# User-Agent 인터넷에서 받아와야함
url = 'http://nadocoding.tistory.com'
headers = {"User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
res = requests.get(url, headers = headers)
res.raise_for_status()  

with open('mygoogle.html', 'w', encoding = 'utf = 8') as f: f.write(res.text)
