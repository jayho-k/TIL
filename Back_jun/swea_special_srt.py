'''
선택
인덱스 짝수 = 큰
인덱스 홀수 = 작

'''

T = int(input())
for tc in range(1, T+1):

    n = int(input())
    lst = list(map(int, input().split()))

    for i in range(len(lst)):
        mn_idx = i
        mx_idx = i

        if i%2==0:
            # 제일 큰수 찾고 교환
            for mx in range(i,len(lst)):
                if lst[mx_idx] < lst[mx]:
                    lst[mx_idx], lst[mx] = lst[mx], lst[mx_idx]

        elif i%2==1:
            # 제일 작은 수 찾고 교환
            for mn in range(i, len(lst)):
                if lst[mn_idx] > lst[mn]:
                    lst[mn_idx], lst[mn] = lst[mn], lst[mn_idx]
                    
    ans_lst = []
    for a in range(10):
        ans_lst.append(lst[a])

    ans = ' '.join(map(str, ans_lst))
    print(f'#{tc} {ans}')