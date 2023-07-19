'''
2,3,4,4,6
M = 8이면 8번을 더하라는 뜻
K = 3일면 중복해서 3번을 더 할 수 있다는 뜻

=> 6 6 6 5 6 6 6 5 => 46

입력예시
5 8 3
2 4 5 4 6
'''

N, M, K = map(int,input().split())
lst = list(map(int, input().split()))

lst.sort()
lst_srt = lst[::-1]
lst_srt = lst_srt[0:2]
# first = lst[-1]
# first = lst[-2]



nanugi = K + 1
total = 0
for i in range(1,M+1):
    # 인덱스 0을 k번 더하고 1을 한번 더하고
    # i => 1%3 1  2 3%3 ==> 0  //      4            5 

    if i%nanugi != 0:
        total += lst_srt[0]

    else:
        total += lst_srt[1]

    print(total)

