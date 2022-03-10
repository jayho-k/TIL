'''
2
1 3
2 5

1
2
1 3
2 5
5
1
2
3
4
5
'''

T = int(input())

for tc in range(1, T+1):
    
    n = int(input())
    lsts = [list(map(int,input().split())) for _ in range(n)]

    
    # c_lst = [int(input()) for _ in range(c)]

    base = [0] * 5001

    for lst in lsts:
        for i in range(lst[0], lst[1]+1):
            base[i] += 1

    # print(base)
    ans = []
    c = int(input())
    for _ in range(c):
        n = int(input())
        ans.append(base[n])

    print(ans)






# T = int(input())
# for tc in range(1, T+1):
#     n = int(input())

#     lst = []
#     for _ in range(n):
#         mn,mx = map(int, input().split())
#         k = list(range(mn, mx+1))
#         lst.append(k)


#     c = int(input())
#     c_lst = [int(input()) for _ in range(c)]

#     # print(c_lst)
    
#     k_lst = list(set(sum(lst, [])))
#     k_mx = max(k_lst)
#     k_mn = min(k_lst)
#     v_lst = [0]*(k_mx-k_mn+1)
  
#     # print(k_lst)
#     # print(v_lst)

#     d = dict(zip(k_lst, v_lst))
#     for l in lst:
#         for i in l:
#             d[i] += 1

#     # print(d)

#     ans_lst = [d[num] for num in c_lst]
#     ans = ' '.join(map(str,ans_lst))
#     print(f'#{tc} {ans}')





# T = int(input())
# for tc in range(1, T+1):
#     N= int(input())
#     stop = [list(map(int, input().split())) for _ in range(N)]
#     #각각의 버스 구간을 리스트로 저장
#     P = int(input())
#     C = [int(input()) for _ in range(P)]
#     cnt = [0] * 5001 #각 정류장별로 지나가는 버스 카운트
      
#     for interval in stop:
#         for j in range(interval[0], interval[1]+1):
#             cnt[j] += 1
#     print(f'#{tc}', end='')
#     for num in C:
#         print(f' {cnt[num]}', end='')
#     print()