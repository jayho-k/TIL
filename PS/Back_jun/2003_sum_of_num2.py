'''
투포인터를 이용할 것이다
부분합 = area_num
area_num >= m ==> st+=1  ==> 스타트 부분만 빼주면 된다.
area_num >= m ==> end += 1 ==>  end부분만 더해주면 된다
'''

n, m = map(int, input().split())
lst = list(map(int, input().split()))
area_sum = 0
end = 0
cnt = 0
for st in range(n):

    while area_sum < m and end < n:

        area_sum += lst[end]
        end += 1

    if area_sum == m:
        cnt += 1

    area_sum -= lst[st]

print(cnt)