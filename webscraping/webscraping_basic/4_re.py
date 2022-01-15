# 정규화 re자료 = w3school사이트에서 궁금한 것들을 찾는다// python re

# re(정규식) : 제대로 된 형태인지 확인하는 것
# ex) 이메일, 주민등록번호, 차량번호, ip주소(3숫자와 3개의 점)

import re
# 차량번호의 기억: ca?e --> ?? 나머지 알파벳 찾기

p = re.compile('ca.e')
# . (ca.e): 하나의 문자를 의미 > ca.e = cafe? caae? // caffe(x)
# ^ (^de): 문자열의 시작 > desk, destination 등등 // fade(x)
# & (se$): 뮨자열의 끝 > case, base (o)

def print_match(m):
    if m:
        print('m.group() :', m.group()) # 일치하는 문자열 반환
        print('m.string : ',m.string)   # 입력받은 문자열  (괄호없이 사용해야한다.)
        print('m.start : ',m.start())   # 일치하는 문자열의 시작 index
        print('m.end() : ',m.end())       # 일치하는 문자열의 끝 index
        print('m.span() : ',m.span()) 

    else:
        print("매치되지 않았습니다.")

# m = p.match("case") 
#     # 매치가 된다. 주어진 문자열의 처음부터 일치하는지 확인
#     # 따라서 careless도 매치한다고 나온다.
# print_match(m)

# m = p.search('good care') 
# # search : 주어진 문자열 중에 일치하는게 있는지 확인
# # match  : 주어진 문자열의 처음부터 일치하는지 확인

# print_match(m)

lst = p.findall('good care cafe') # findall: 일치하는 모든 것을 리스트 형태로 반환
print(lst) # ['care', 'cafe']

# 1. p = re.compile('원하는 형태')
# 2. m = p.match('비교할 문자열')
# 3. m = p.search('비교할 문자열')
# 4. lst = p.findall('비교할 문자열')

# 원하는 형태: 정규식
# . (ca.e): 하나의 문자를 의미 > ca.e = cafe? caae? // caffe(x)
# ^ (^de): 문자열의 시작 > desk, destination 등등 // fade(x)
# & (se$): 뮨자열의 끝 > case, base (o)

