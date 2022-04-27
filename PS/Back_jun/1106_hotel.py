'''
비용, 늘어나는 고객의 수

10 3
3 1
2 2
1 3

'''

c, n = map(int,input().split())

# 비용, 늘어나는 고객의 수
lst = [list(map(int,input().split())) for _ in range(n)]
table = [1e9]*(101+c)


ans = 1e9
for cost,cus in lst:

    table[cus] = cost
    for i in range(0,101+c):
        table[i] = min(table[i], table[i-cus]+cost)

        if c <= i:
            ans = min(table[i],ans)

    print(table[:c+5])


# print(table)
# print(table[c])
print(ans)
