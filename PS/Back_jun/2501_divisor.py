'''
그래서 6의 약수는 1, 2, 3, 6, 총 네 개이다.

두 개의 자연수 N과 K가 주어졌을 때, N의 약수들 중 K번째로 작은 수를 출력하는 프로그램을 작성하시오.

2735 1
6 3
25 4
'''

n,k = map(int,input().split())

num = 0
ans = 0
for i in range(1,n+1):
    if n%i == 0:
        num += 1

        if num == k:
            ans = i
            break

if ans == 0:
    print(0)
else:
    print(ans)
    
