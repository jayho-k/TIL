'''
대각선 운동
대각선은 가로 1늘어나고 세로 1늘어는거다
따로따로 생각해서 하면 된다

6x4 이고 x값만 한다면
p= 6x2
나머지 => t+좌표 % p
6보다 나머지가 클때와 안클떄로 나눠준다

'''
import sys

x, y = map(int, sys.stdin.readline().split())
x1,y1 = map(int, sys.stdin.readline().split())
t = int(sys.stdin.readline())

px = x*2
py = y*2

Xnamuzi = (t+x1)%px
Ynamuzi = (t+y1)%py

if x < Xnamuzi:
    Xnamuzi = px - Xnamuzi

if y < Ynamuzi:
    Ynamuzi = py - Ynamuzi

print(Xnamuzi, Ynamuzi)





