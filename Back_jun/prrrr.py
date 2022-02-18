T = int(input())
 
for tc in range(1, T+1):
     
    n = int(input())
     
    mx = 0
    mn = 1000000
    lsts = []
    for _ in range(n):
        imn,imx = map(int, input().split())
        lsts.append(list(range(imn, imx+1)))
        if mn > imn:
            mn = imn
        if mx < imx:
            mx = imx
     
    c = int(input())
    c_lst = [int(input()) for _ in range(c)]
 
 
    base = [0] * (mx+1)
 
    for lst in lsts:
        for l in lst:
            base[l] += 1

    print()
    ans = []
    for i in c_lst:
        ans.append(base[i])
    s = ' '.join(map(str,ans))
    print(f'#{tc} {s}')
     
    # ans = ' '.join(map(str, base[1:]))
 
    # print(f'#{tc} {ans}')