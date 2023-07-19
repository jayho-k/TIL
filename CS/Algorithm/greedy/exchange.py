'''
500, 100, 50, 10원
거슬러 줘야할 돈이 N원일떄 거슬러 줘야할 동전의 최소개수를 구하라

ex) 1260원의 최소 개수

큰 단위부터 나누어 떨어질 때 까지
'''
cost = 1260

coin_type = [500, 100, 50, 10]

n = 0
for i in coin_type:
    n += cost//i
    cost = cost%i
    print(cost)

print(n)

