import requests
# from bs4 import BeautifulSoup

url = 'https://api.agify.io'


for name in ['ga','df']:
    params ={
        'name' : name
    }
    res = requests.get(url, params = params).json()
    print(res)


# base_url = 'https://developers.themoviedb.org/3'
# path = '/movie/now_playing'

# # 'https://developers.themoviedb.org/3/movie/now_playing> api_key = 'dddddd&region=KR&language=ko'

# params = {
#     'api_key': '50ca281a943ecad26f13d17bc9d40827',
#     'region' : 'KR',
#     'language':'ko'
# }
# # url로 만들면 더 쉽게 볼 수 있음
# res = requests.get(base_url+path, params = params).json()

# # url로 보는 방법
# # res = requests.get(base_url+path, params = params)
# # print(res.status_code, response.url)
# # data = response.json()

# print(res)