"""
5
10 20 30 40 50
5
1 3
2 4
3 5
1 5
4 4

"""

n = int(input())
lst = list(map(int,input().split()))
sum_lst = [0]
for i in range(n):
    sum_lst.append(lst[i]+sum_lst[-1])

#print(sum_lst)

m = int(input())
for _ in range(m):
    s,e = map(int,input().split())
    print(sum_lst[e] - sum_lst[s-1])
