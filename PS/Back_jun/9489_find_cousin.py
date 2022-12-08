'''

12 9
3 5 6 8 9 10 13 15 16 22 23 25
10 4
1 3 4 5 8 9 15 30 31 32
0 0


+2 level => 같은 부모인 경우 cousin

10 15
1 3 4 5 8 9 15 30 31 32

'''



while 1:
    n,target = map(int,input().split())
    if n == 0 and target == 0:
        break

    val = [-1]+list(map(int,input().split()))
    cnt = -1
    parents = [0]*(n+1)
    t = 0

    for i in range(1,len(val)):
        if val[i] == target:
            t = i

        # find parents
        if val[i]-1 != val[i-1]:
            cnt += 1
            parents[i] = val[cnt]
        else:
            parents[i] = val[cnt]


    tmp_idx = val.index(parents[t])
    grand = parents[tmp_idx]
    tmp_idx_lst = set()
    ans = 0
    for j in range(len(val)):
        if parents[j] == grand and j != tmp_idx:
            tmp_idx_lst.add(val[j])
        
        if parents[j] in tmp_idx_lst:
            ans += 1
    print(ans)