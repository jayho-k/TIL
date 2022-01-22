
# while은 따라 항상 break를 걸어주어야 한는 것 같음
# 따로 숫자가 주어지지 않을 경우에
# While 1 은 참이라는 뜻이다

#1. text값이 주어지지 않을 경우에는 따라 에러를 발생시켜주어야 한다
while 1:
    try:
        x,y = map(int, input().split())
        print(x+y)
    except:
        break

#2. x와 y가 0일 경우 멈추기
while 1:
    x, y = map(int,input().split())
    if x == 0 and y == 0:
        break
    else:
        print(x+y)