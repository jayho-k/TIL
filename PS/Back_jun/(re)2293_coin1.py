'''

n가지 종류의 동전이 있다. 각각의 동전이 나타내는 가치는 다르다. 이 동전을 적당히 사용해서, 그 가치의 합이 k원이 되도록 하고 싶다. 그 경우의 수를 구하시오. 각각의 동전은 몇 개라도 사용할 수 있다.

사용한 동전의 구성이 같은데, 순서만 다른 것은 같은 경우이다.

3 10
1
2
5
'''

n,knum = map(int,input().split())
lst = [int(input()) for _ in range(n)]

dp = [0]*(10001)
dp[0] = 1

for l in lst:
    for k in range(1,knum+1):
        
        if l<=k:
            dp[k] = dp[k-l]+dp[k]

print(dp[knum])