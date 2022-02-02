'''
1. 로봇개수 n, 반지름 r
2. 로봇 위치 a b (-1000,1000) ==> 0,0은 없음
3. 손님 수 m (1,10000) 
4. 손님 위치 c,d ==> 0,0은 없음

==> 중복이 되는 경우는?

'''
n, r = map(int, input().split())
r_lst = []
for i in range(n):
    a, b = map(int, input().split())
    r_lst.append((a,b))


m = int(input())
h_lst = []
for i in range(m):
    c, d = map(int, input().split())
    h_lst.append((c,d))


cnt = 0
for h_lo in h_lst:

    h_lo_x, h_lo_y = h_lo

    for r_lo in r_lst:
        r_lo_x, r_lo_y = r_lo

        dx = r_lo_x - r_lo_x
        dy = r_lo_y - h_lo_y

        dist = dx**2 + dy**2

        if dist > r**2:
            cnt += 1
            break

print(cnt)


'''
2 2
0 0
-1 -1
4
1 1
1 2
3 3
5 5

3

3 3
2 1
4 4
2 4
5
4 4
4 1
5 4
0 1
1 4

0
'''