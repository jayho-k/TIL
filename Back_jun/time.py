'''
모든 시각중에서 3이 하나라도 포함되는 경우의 수

00시00분00초 ~ N시 59분 59초

'''

hour = int(input())
min = 60
sec = 60

cnt = 1
for h in range(hour+1):
    for m in range(min):
        for s in range(sec):
            if '3' in str(h) + str(m) + str(s):
                cnt += 1 
        

print(cnt)