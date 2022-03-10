'''
10개의 정수를 받는다
부분 집합의 합이 0이 되는 것이 존재하는지를 계산하는 함수
존재하면 1
존재 안하면 0


'''

T = int(input())
for tc in range(1,T+1):
    lst = list(map(int, input().split()))
    n = len(lst)

    p = []
    for i in range(1<<n):
        t = []
        for j in range(n):
            if i & (1<<j):
                t.append(lst[j])
        if t == []:
            continue
        
        sm = sum(t)
        if sm == 0:
            print(f'#{tc} {1}')
            break

    else:
        print(f'#{tc} {0}')












# arr = [3,6,7,1,5,4] #2의6승 ==> 64개

# n = len(arr)

# for i in range(1<<n):
#     # print(bin(i)) # 0, 1, 10, 11, 100, 101, 110, 111
    
#     for j in range(n):
#         if i & (1<<j):
            
#             print(arr[j], end=' ')
#     print()

# print()