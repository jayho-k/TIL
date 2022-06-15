'''
n

4
1 2 3 4 5 6 7 8 9 1000
338 304 619 95 343 496 489 116 98 127
931 240 986 894 826 640 965 833 136 138
940 955 364 188 133 254 501 122 768 408
'''

T = int(input())
for tc in range(1,T+1):

    lst = list(map(int,input().split()))

    tmp = [0]*1001
    for i in lst:
        tmp[i] += 1

    for j in range(1,1001):
        tmp[j] += tmp[j-1]
    
    ans = [0]*tmp[-1]

# 338 304 619 95 343 496 489 116 98 127
    for num in lst:
        idx = tmp[num]
        ans[idx-1] = num
        tmp[num] -= 1

    # print(tmp)
    # print(ans)
    print(ans[-3])

