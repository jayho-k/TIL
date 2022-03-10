'''
로직 => 동서남북을 펼친다 ==> 그다음에 위치선정 뒤에 ==> index로 거리를 확인 후 ==> 크고작은 값을 반환

1. 가로세로
2. 상점의 개수
3. 한줄에 하나씩 상점의 위치 , 개수
    3-1 (1북,2남,3서,4동)
    3-2 북남 => 왼쪽 기준 거리, 서동 => 북쪽 기준 거리
4. 동근이의 위치(같은 방식)

'''

garo, sero = map(int, input().split())
s_num = int(input())

n = [0]*(garo)
e = [0]*(sero)
w = [0]*(sero)
s = [0]*(garo)

di_lst = [0,n,s,w,e]

for i in range(1,s_num+1):
    di, far = map(int, input().split())
    if di == 1 or di == 4:
        di_lst[di][far] = i
    else:
        di_lst[di][-far] = i 
        # 이것이 포인트인데 ==> 이게 동서남북을 붙일때 붙어 있는 부분이 생긴다
        # 북동을 붙일 때 1번 겹침, 동남에서 한번 또 겹침 그래서 그냥 한칸씩 땡겨 주기 위해서 -far -1을 안하고
        # - far를 하여 1칸씩 땡겨오는 작업이다.

x_di, x_far = map(int, input().split())
if x_di == 1 or x_di == 4:
        di_lst[x_di][x_far] = 101 # 걔 동근이
else:
    di_lst[x_di][-x_far] = 101

grid = (n+e+s+w)*2

sv = []
for i in range(1,s_num+1):
    a = abs(grid.index(101)-grid.index(i))
    b = abs(2*(garo+sero)-a)

    if a >= b:
        sv.append(b)
    else:
        sv.append(a)
print(sum(sv))
