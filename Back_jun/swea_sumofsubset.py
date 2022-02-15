'''
일단 부분집합 합을 구현해주자

'''



T = int(input())
for tc in range(1, T+1):

    n, k = map(int, input().split()) 

    lst = list(range(1,12+1))
    nn = len(lst)

    p_lsts = []
    for i in range(1<<nn):
        temp_lsts = []
        tmp_cnt = 0
        tmp_sum = 0

        for j in range(nn):
            if i & (1<<j):
                temp_lsts.append(lst[j])
                # if len(lst) == n and tmp_sum == k:
                #     tmp_sum += j+1
                #     tmp_cnt += 1

        p_lsts.append(temp_lsts)

    # print(tmp_sum)
    # print(tmp_cnt)

        

    cnt = 0
    for p in p_lsts:
        sm = sum(p)
        l =len(p)
        if l == n and sm == k:
            cnt += 1
        
    print(f'#{tc} {cnt}')