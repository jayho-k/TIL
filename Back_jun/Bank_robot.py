'''
1. 로봇개수 n, 반지름 r
2. 로봇 위치 a b (-1000,1000)
3. 손님 수 m (1,10000) 
4. 손님 위치 c,d

==> 중복이 되는 경우는?

'''
n, r = map(int, input().split())
r_lst = []
for i in range(n):
    a, b = map(int, input().split())
    r_lst.append((a,b))

r_lst = list(set(r_lst))

m = int(input())
h_lst = []
for i in range(m):
    c, d = map(int, input().split())
    h_lst.append((c,d))

cnt = m
for h_lo in h_lst:

    h_lo_x, h_lo_y = h_lo

    for r_lo in r_lst:
        r_lo_x, r_lo_y = r_lo

        dx = abs(r_lo_x - h_lo_x)
        dy = abs(r_lo_y - h_lo_y)

        dist = dx**2 + dy**2

        # 아무도 안걸렸을때 -1 을 할꺼야

        if dist <= r**2:
            cnt -= 1
            break

print(cnt)

# lst = [(1,2), (1,2)]

# a = list(set(lst))
# print(a)




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