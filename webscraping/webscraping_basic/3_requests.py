import requests
res = requests.get("http://google.com")
print('응답코드 :', res.status_code) # 200이면 정상// 403 = 페이지에 가져올 권한이 없다
res.raise_for_status()  # 아래처럼 if문을 쓰지 않더라도 에러를 뜨게 만들어주는 함수

# if res.status_code == requests.codes.ok: # 괜찮으면 정상// 아니면 문제 발생
#     print("정상")
# else:
#     print("문제발생. 에러코드", res.status_code)

print(len(res.text))

with open('mygoogle.html', 'w', encoding = 'utf = 8') as f: f.write(res.text)
# 원하는 페이지에  접속하고 파일로 만들어보기
