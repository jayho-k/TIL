'''
3
0.625
0.1
0.125

소수를 이진수로 바꾸기
'''
T = int(input())
for tc in range(1,T+1):
    n = float(input())
    lst = []

    s = n
    for _ in range(30):
        s = 2*s
        m = int(s)
        lst.append(m)
        s = (s-m)

    if 1 in lst[12:]:
        print(f'#{tc} overflow')   

    else:
        for i in range(len(lst)-1,-1,-1):
            if lst[i] == 1:
                ans_lst = lst[:i+1]
                break

        ans = ''.join(map(str,ans_lst))
        print(f'#{tc} {ans}')