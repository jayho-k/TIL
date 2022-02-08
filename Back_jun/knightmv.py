'''
행위치 : 숫자
열위치 : 알파벳

알파벳이 바뀌면 좌우로
숫자가 바뀌면 위아래로 움직임

카운트 세보면 된다

'''
x, y = list(input()) # 초기값 설정 완료
y = int(y)
x = int(ord(x)-ord('a')) + 1  # 이거 미침!!

btn = [(-2,-1),(-2,1),(2,-1),(2,1),(-1,-2),(1,-2),(-1,2),(1,2)] #가지 방법

cnt = 0

for b in btn:
    nx, ny = b

    dx = x + nx
    dy = y + ny

    if 1 <= dx <= 8 and 1 <= dy <= 8:
        cnt += 1

print(cnt)
