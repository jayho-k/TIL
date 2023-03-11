'''

2     
10 40 100 300   
0 0 2 9 1 5 0 0 0 0 0 0
10 100 50 300   
0 0 0 0 0 0 0 0 6 2 7 8

'''

for tc in range(1,int(input())+1):

    d,m,q,y = map(int,input().split())
    month = list(map(int,input().split()))
    dp = [y]+[0]*(len(month))
    qua = 1e9

    for i in range(len(month)-1,-1,-1):
        day = d*month[i]+dp[i+1]
        mon = m+dp[i+1]
        if i+3<=12: qua = q+dp[i+3]
        dp[i]=min(day,mon,qua,y)
    print(f"#{tc} {dp[0]}")